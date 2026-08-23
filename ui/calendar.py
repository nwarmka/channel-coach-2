# Channel Coach - Content Calendar UI

import calendar as pycalendar
import html
from datetime import date, timedelta

import gradio as gr

from features import (
    CONTENT_TYPES,
    CONTENT_STATUSES,
    add_content_item,
    delete_content_item,
    get_calendar_choices,
    load_content_calendar,
    load_selected_content_item,
    plan_my_week,
    render_content_calendar,
    render_upcoming_content,
    update_content_item,
)


def _month_heading(month, year):
    return f"## {pycalendar.month_name[int(month)]} {int(year)}"


def _six_week_dates(month, year):
    month = int(month)
    year = int(year)
    cal = pycalendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)
    while len(weeks) < 6:
        start = weeks[-1][-1] + timedelta(days=1)
        weeks.append([start + timedelta(days=i) for i in range(7)])
    return [day for week in weeks[:6] for day in week]


def _filtered_items(workspace_name, status_filter, type_filter):
    items = load_content_calendar(workspace_name)
    if status_filter != "All":
        items = [item for item in items if item.get("status") == status_filter]
    if type_filter != "All":
        items = [item for item in items if item.get("content_type") == type_filter]
    return items


def _cell_text(day, visible_month, items):
    day_items = [
        item for item in items
        if item.get("publish_date") == day.isoformat()
    ]

    if day.month == int(visible_month):
        first_line = str(day.day)
    else:
        first_line = f"{pycalendar.month_abbr[day.month]} {day.day}"

    lines = [first_line]
    for item in day_items[:3]:
        title = (item.get("title") or "Untitled").strip()
        if len(title) > 22:
            title = title[:19] + "..."
        lines.append(title)

    if len(day_items) > 3:
        lines.append(f"{len(day_items) - 3} more")

    return "\n".join(lines)


def _day_button_updates(workspace_name, month, year, status_filter, type_filter):
    items = _filtered_items(workspace_name, status_filter, type_filter)
    dates = _six_week_dates(month, year)
    return [
        gr.update(value=_cell_text(day, month, items))
        for day in dates
    ]


def _refresh_cells(workspace_name, month, year, status_filter, type_filter):
    return _day_button_updates(
        workspace_name, month, year, status_filter, type_filter
    )


def _move_month(workspace_name, month, year, status_filter, type_filter, delta):
    month = int(month)
    year = int(year)
    month += delta
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    return (
        month,
        year,
        _month_heading(month, year),
        *_day_button_updates(
            workspace_name, month, year, status_filter, type_filter
        ),
    )


def _prev_month(workspace_name, month, year, status_filter, type_filter):
    return _move_month(
        workspace_name, month, year, status_filter, type_filter, -1
    )


def _next_month(workspace_name, month, year, status_filter, type_filter):
    return _move_month(
        workspace_name, month, year, status_filter, type_filter, 1
    )


def _today_month(workspace_name, status_filter, type_filter):
    today = date.today()
    return (
        today.month,
        today.year,
        _month_heading(today.month, today.year),
        *_day_button_updates(
            workspace_name,
            today.month,
            today.year,
            status_filter,
            type_filter,
        ),
    )


def _open_day(index, workspace_name, month, year, status_filter, type_filter):
    selected = _six_week_dates(month, year)[int(index)]
    items = _filtered_items(workspace_name, status_filter, type_filter)
    day_items = [
        item for item in items
        if item.get("publish_date") == selected.isoformat()
    ]

    heading = f"## {selected.strftime('%A, %B')} {selected.day}, {selected.year}"

    chunks = ['<div class="cc-day-view-list">']
    if not day_items:
        chunks.append(
            '<div class="cc-day-empty">Nothing scheduled for this day yet.</div>'
        )
    else:
        for item in day_items:
            title = html.escape(item.get("title", "Untitled"))
            status = html.escape(item.get("status", "Idea"))
            content_type = html.escape(item.get("content_type", "Long Video"))
            topic = html.escape(item.get("game_topic", ""))
            chunks.append(
                '<div class="cc-open-day-event">'
                f'<strong>{title}</strong>'
                f'<span>{status} · {content_type}</span>'
                + (f'<span>{topic}</span>' if topic else '')
                + '</div>'
            )
    chunks.append('</div>')

    return (
        gr.update(visible=False),
        gr.update(visible=True),
        heading,
        "".join(chunks),
        selected.isoformat(),
    )


def _make_day_handler(index):
    def handler(workspace_name, month, year, status_filter, type_filter):
        return _open_day(
            index,
            workspace_name,
            month,
            year,
            status_filter,
            type_filter,
        )
    return handler


def _back_to_month():
    return gr.update(visible=True), gr.update(visible=False)


def build_calendar_page(workspace_name, visible=False):
    today = date.today()

    with gr.Column(visible=visible, elem_id="calendar-page") as calendar_page:

        gr.HTML(
            """
            <style>
              #calendar-page {
                  max-width: 1280px;
                  margin: 0 auto;
              }

              #calendar-page .cc-calendar-subtitle {
                  opacity: .72;
                  margin-bottom: 14px;
              }

              #calendar-page .cc-toolbar {
                  border: 1px solid rgba(255,62,165,.32);
                  border-radius: 16px;
                  background: rgba(7,10,17,.88);
                  padding: 12px 14px;
                  margin-bottom: 14px;
              }

              #calendar-page .cc-card {
                  border: 1px solid rgba(255,62,165,.32);
                  border-radius: 16px;
                  background: rgba(7,10,17,.88);
                  padding: 18px;
              }

              #calendar-page .cc-nav-row {
                  align-items: center;
                  gap: 8px;
              }

              #calendar-page .cc-month-heading h2 {
                  margin: 0;
              }

              #calendar-page .cc-month-grid {
                  padding: 0;
                  overflow: hidden;
              }

              #calendar-page .cc-weekday-row,
              #calendar-page .cc-day-row {
                  gap: 0 !important;
              }

              #calendar-page .cc-weekday-label {
                  text-align: center;
                  font-size: 12px;
                  font-weight: 700;
                  opacity: .78;
                  padding: 8px 0;
                  margin: 0;
              }

              #calendar-page .cc-day-button {
                  min-width: 0 !important;
                  margin: 0 !important;
              }

              #calendar-page .cc-day-button button {
                  min-height: 128px !important;
                  border-radius: 0 !important;
                  border: 1px solid rgba(148,163,184,.22) !important;
                  background: rgba(8,12,22,.72) !important;
                  white-space: pre-line !important;
                  text-align: left !important;
                  justify-content: flex-start !important;
                  align-items: flex-start !important;
                  padding: 10px !important;
                  line-height: 1.45 !important;
                  font-weight: 600 !important;
                  cursor: pointer !important;
              }

              #calendar-page .cc-day-button button:hover {
                  background: rgba(139,92,246,.14) !important;
                  border-color: rgba(139,92,246,.70) !important;
              }

              #calendar-page .cc-open-day-view {
                  min-height: 520px;
              }

              #calendar-page .cc-day-back {
                  max-width: 180px;
                  margin-bottom: 8px;
              }

              #calendar-page .cc-day-view-list {
                  display: flex;
                  flex-direction: column;
                  gap: 10px;
                  margin-top: 12px;
              }

              #calendar-page .cc-open-day-event {
                  display: flex;
                  flex-direction: column;
                  gap: 4px;
                  padding: 12px 14px;
                  border-left: 4px solid #8b5cf6;
                  border-radius: 8px;
                  background: rgba(139,92,246,.10);
              }

              #calendar-page .cc-open-day-event span,
              #calendar-page .cc-day-empty {
                  opacity: .74;
              }

              @media (max-width: 760px) {
                  #calendar-page .cc-day-button button {
                      min-height: 86px !important;
                      padding: 6px !important;
                      font-size: 12px !important;
                  }
              }
            </style>

            <h2>📅 Content Calendar</h2>
            <div class="cc-calendar-subtitle">
                Click any date to open that day.
            </div>
            """
        )

        calendar_month = gr.State(today.month)
        calendar_year = gr.State(today.year)

        with gr.Row(elem_classes=["cc-toolbar", "cc-nav-row"]):
            calendar_prev_button = gr.Button("←", min_width=44)
            calendar_today_button = gr.Button("Today", min_width=90)
            calendar_next_button = gr.Button("→", min_width=44)

            month_heading = gr.Markdown(
                _month_heading(today.month, today.year),
                elem_classes=["cc-month-heading"],
            )

            calendar_status_filter = gr.Dropdown(
                ["All"] + CONTENT_STATUSES,
                value="All",
                label="Status",
            )

            calendar_type_filter = gr.Dropdown(
                ["All"] + CONTENT_TYPES,
                value="All",
                label="Type",
            )

        with gr.Column(
            visible=True,
            elem_classes=["cc-card", "cc-month-grid"],
        ) as month_grid_view:

            with gr.Row(elem_classes=["cc-weekday-row"]):
                for name in ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]:
                    gr.Markdown(name, elem_classes=["cc-weekday-label"])

            initial_items = _filtered_items("main", "All", "All")
            initial_dates = _six_week_dates(today.month, today.year)

            day_buttons = []
            for row in range(6):
                with gr.Row(elem_classes=["cc-day-row"]):
                    for col in range(7):
                        idx = row * 7 + col
                        day_buttons.append(
                            gr.Button(
                                _cell_text(
                                    initial_dates[idx],
                                    today.month,
                                    initial_items,
                                ),
                                elem_classes=["cc-day-button"],
                                min_width=0,
                                scale=1,
                            )
                        )

        with gr.Column(
            visible=False,
            elem_classes=["cc-card", "cc-open-day-view"],
        ) as day_view:
            day_back_button = gr.Button(
                "← Back to month",
                elem_classes=["cc-day-back"],
            )
            day_view_heading = gr.Markdown("## Day")
            day_details_output = gr.HTML(
                '<div class="cc-day-empty">Nothing scheduled for this day yet.</div>'
            )

        # IMPORTANT: backend compatibility only.
        # This old HTML calendar is hidden so it can no longer cover or replace
        # the real clickable Gradio calendar above.
        calendar_output = gr.HTML(
            value=render_content_calendar(
                today.month,
                today.year,
                "All",
                "All",
                user_id="main",
            ),
            visible=False,
        )

        gr.Markdown("### Content tools")

        with gr.Row(equal_height=False):
            with gr.Column(scale=1, min_width=300, elem_classes=["cc-card"]):
                gr.Markdown("### ➕ Add Content")

                calendar_title = gr.Textbox(
                    label="Title",
                    placeholder="Example: Getting the Ice Rod",
                )
                calendar_content_type = gr.Dropdown(
                    CONTENT_TYPES,
                    value="Long Video",
                    label="Content Type",
                )
                calendar_game_topic = gr.Textbox(
                    label="Game / Topic",
                    placeholder="Example: Zelda ALTTP",
                )
                calendar_status = gr.Dropdown(
                    CONTENT_STATUSES,
                    value="Idea",
                    label="Status",
                )
                calendar_publish_date = gr.Textbox(
                    label="Target Publish Date",
                    value=today.isoformat(),
                    placeholder="YYYY-MM-DD",
                )
                calendar_notes = gr.Textbox(
                    label="Notes",
                    lines=4,
                )
                calendar_add_button = gr.Button("➕ Add to Calendar")
                calendar_message = gr.Textbox(
                    show_label=False,
                    placeholder="Calendar status",
                    lines=2,
                )

            with gr.Column(scale=1, min_width=300, elem_classes=["cc-card"]):
                gr.Markdown("### 🔥 Coming Up")
                upcoming_output = gr.HTML(
                    value=render_upcoming_content(user_id="main")
                )
                plan_week_button = gr.Button("✨ Plan My Week")
                plan_week_output = gr.Textbox(
                    show_label=False,
                    placeholder="Weekly content plan",
                    lines=12,
                )

        gr.Markdown("### ✏️ Edit or Delete Content")

        with gr.Column(elem_classes=["cc-card"]):
            calendar_item_picker = gr.Dropdown(
                choices=get_calendar_choices("main"),
                label="Choose Calendar Item",
            )
            calendar_load_button = gr.Button("📂 Load Selected Item")
            with gr.Row():
                calendar_update_button = gr.Button("💾 Save Edit")
                calendar_delete_button = gr.Button("🗑️ Delete Selected Item")

        refresh_inputs = [
            workspace_name,
            calendar_month,
            calendar_year,
            calendar_status_filter,
            calendar_type_filter,
        ]

        nav_outputs = [
            calendar_month,
            calendar_year,
            month_heading,
            *day_buttons,
        ]

        calendar_prev_button.click(
            _prev_month,
            inputs=refresh_inputs,
            outputs=nav_outputs,
        )

        calendar_next_button.click(
            _next_month,
            inputs=refresh_inputs,
            outputs=nav_outputs,
        )

        calendar_today_button.click(
            _today_month,
            inputs=[
                workspace_name,
                calendar_status_filter,
                calendar_type_filter,
            ],
            outputs=nav_outputs,
        )

        calendar_status_filter.change(
            _refresh_cells,
            inputs=refresh_inputs,
            outputs=day_buttons,
        )

        calendar_type_filter.change(
            _refresh_cells,
            inputs=refresh_inputs,
            outputs=day_buttons,
        )

        for index, button in enumerate(day_buttons):
            button.click(
                _make_day_handler(index),
                inputs=refresh_inputs,
                outputs=[
                    month_grid_view,
                    day_view,
                    day_view_heading,
                    day_details_output,
                    calendar_publish_date,
                ],
                show_progress="hidden",
            )

        day_back_button.click(
            _back_to_month,
            inputs=None,
            outputs=[month_grid_view, day_view],
            show_progress="hidden",
        )

        add_event = calendar_add_button.click(
            add_content_item,
            inputs=[
                calendar_title,
                calendar_content_type,
                calendar_game_topic,
                calendar_status,
                calendar_publish_date,
                calendar_notes,
                workspace_name,
                calendar_month,
                calendar_year,
                calendar_status_filter,
                calendar_type_filter,
            ],
            outputs=[
                calendar_output,
                upcoming_output,
                calendar_item_picker,
                calendar_message,
            ],
        )

        calendar_load_button.click(
            load_selected_content_item,
            inputs=[calendar_item_picker, workspace_name],
            outputs=[
                calendar_title,
                calendar_content_type,
                calendar_game_topic,
                calendar_status,
                calendar_publish_date,
                calendar_notes,
                calendar_message,
            ],
        )

        update_event = calendar_update_button.click(
            update_content_item,
            inputs=[
                calendar_item_picker,
                calendar_title,
                calendar_content_type,
                calendar_game_topic,
                calendar_status,
                calendar_publish_date,
                calendar_notes,
                workspace_name,
                calendar_month,
                calendar_year,
                calendar_status_filter,
                calendar_type_filter,
            ],
            outputs=[
                calendar_output,
                upcoming_output,
                calendar_item_picker,
                calendar_message,
            ],
        )

        delete_event = calendar_delete_button.click(
            delete_content_item,
            inputs=[
                calendar_item_picker,
                workspace_name,
                calendar_month,
                calendar_year,
                calendar_status_filter,
                calendar_type_filter,
            ],
            outputs=[
                calendar_output,
                upcoming_output,
                calendar_item_picker,
                calendar_message,
            ],
        )

        for event in [add_event, update_event, delete_event]:
            event.then(
                _refresh_cells,
                inputs=refresh_inputs,
                outputs=day_buttons,
                show_progress="hidden",
            )

        plan_week_button.click(
            plan_my_week,
            inputs=[workspace_name],
            outputs=plan_week_output,
            show_progress="full",
        )

    return (
        calendar_page,
        calendar_output,
        upcoming_output,
        calendar_item_picker,
    )


build_calendar_tab = build_calendar_page






      
