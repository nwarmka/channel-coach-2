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
    refresh_content_calendar,
    render_content_calendar,
    render_upcoming_content,
    update_content_item,
)


def _month_heading(month, year):
    return f"## {pycalendar.month_name[int(month)]} {int(year)}"


def _six_week_dates(month, year):
    """Always return 42 visible dates, Sunday through Saturday."""
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


def _calendar_matrix(workspace_name, month, year, status_filter, type_filter):
    """Return a 6x7 list used by the clickable calendar grid."""
    month = int(month)
    year = int(year)
    today = date.today()
    dates = _six_week_dates(month, year)
    items = _filtered_items(workspace_name, status_filter, type_filter)

    cells = []
    for day in dates:
        day_items = [
            item for item in items
            if item.get("publish_date") == day.isoformat()
        ]

        if day.month == month:
            date_text = f"● {day.day}" if day == today else str(day.day)
        else:
            date_text = f"{pycalendar.month_abbr[day.month]} {day.day}"

        lines = [date_text]
        for item in day_items[:3]:
            title = (item.get("title") or "Untitled").strip()
            if len(title) > 24:
                title = title[:21] + "..."
            lines.append(title)

        if len(day_items) > 3:
            lines.append(f"{len(day_items) - 3} more")

        cells.append("\\n".join(lines))

    return [cells[i:i + 7] for i in range(0, 42, 7)]


def _month_refresh(workspace_name, month, year, status_filter, type_filter):
    return _calendar_matrix(
        workspace_name, month, year, status_filter, type_filter
    )


def _move_month_native(
    workspace_name,
    month,
    year,
    status_filter,
    type_filter,
    delta,
):
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
        render_upcoming_content(user_id=workspace_name),
        _calendar_matrix(
            workspace_name, month, year, status_filter, type_filter
        ),
    )


def _previous_month_native(
    workspace_name, month, year, status_filter, type_filter
):
    return _move_month_native(
        workspace_name, month, year, status_filter, type_filter, -1
    )


def _next_month_native(
    workspace_name, month, year, status_filter, type_filter
):
    return _move_month_native(
        workspace_name, month, year, status_filter, type_filter, 1
    )


def _today_month_native(workspace_name, status_filter, type_filter):
    today = date.today()
    return (
        today.month,
        today.year,
        _month_heading(today.month, today.year),
        render_upcoming_content(user_id=workspace_name),
        _calendar_matrix(
            workspace_name,
            today.month,
            today.year,
            status_filter,
            type_filter,
        ),
    )


def _select_calendar_day(
    workspace_name,
    month,
    year,
    status_filter,
    type_filter,
    evt: gr.SelectData,
):
    """Open the date represented by the selected calendar cell."""
    try:
        row_index, col_index = evt.index
        cell_index = int(row_index) * 7 + int(col_index)
        selected = _six_week_dates(month, year)[cell_index]
    except Exception:
        return (
            "### Select a day",
            '<div class="cc-day-empty">Click any date in the calendar.</div>',
            "",
        )

    items = _filtered_items(workspace_name, status_filter, type_filter)
    day_items = [
        item for item in items
        if item.get("publish_date") == selected.isoformat()
    ]

    heading = (
        f"### {selected.strftime('%A, %B')} "
        f"{selected.day}, {selected.year}"
    )

    html_parts = ['<div class="cc-day-view-list">']

    if not day_items:
        html_parts.append(
            '<div class="cc-day-empty">'
            'Nothing scheduled for this day yet.'
            '</div>'
        )
    else:
        for item in day_items:
            title = html.escape(item.get("title", "Untitled"))
            status = html.escape(item.get("status", "Idea"))
            content_type = html.escape(
                item.get("content_type", "Long Video")
            )
            topic = html.escape(item.get("game_topic", ""))

            html_parts.append(
                '<div class="cc-open-day-event">'
                f'<strong>{title}</strong>'
                f'<span>{status} · {content_type}</span>'
                + (f'<span>{topic}</span>' if topic else "")
                + '</div>'
            )

    html_parts.append("</div>")

    return (
        heading,
        "".join(html_parts),
        selected.isoformat(),
    )


def build_calendar_page(workspace_name, visible=False):
    """Build the Content Calendar page and wire all Calendar events."""

    today = date.today()

    with gr.Column(
        visible=visible,
        elem_id="calendar-page",
    ) as calendar_page:

        gr.HTML(
            """
            <style>
              #calendar-page {
                  max-width: 1280px;
                  margin: 0 auto;
              }

              #calendar-page .cc-calendar-subtitle {
                  opacity: .72;
                  margin-bottom: 18px;
              }

              #calendar-page .cc-card,
              #calendar-page .cc-toolbar {
                  border: 1px solid rgba(255,62,165,.32);
                  border-radius: 16px;
                  background: rgba(7,10,17,.88);
              }

              #calendar-page .cc-card {
                  padding: 18px;
              }

              #calendar-page .cc-toolbar {
                  padding: 12px 14px;
                  margin-bottom: 14px;
              }

              #calendar-page .cc-nav-row {
                  align-items: center;
                  gap: 8px;
              }

              #calendar-page .cc-nav-button {
                  min-width: 46px;
              }

              #calendar-page .cc-today-button {
                  min-width: 90px;
              }

              #calendar-page .cc-month-heading h2 {
                  margin: 0;
                  line-height: 1.2;
              }

              #calendar-page .cc-weekday-row,
              #calendar-page .cc-day-row {
                  gap: 0 !important;
              }

              #calendar-page .cc-weekday-label {
                  text-align: center;
                  font-size: 12px;
                  font-weight: 700;
                  opacity: .72;
                  padding: 7px 0;
              }

              #calendar-page .cc-day-button {
                  min-width: 0 !important;
                  margin: 0 !important;
              }

              #calendar-page .cc-day-button button {
                  min-height: 118px !important;
                  border-radius: 0 !important;
                  border: 1px solid rgba(148,163,184,.22) !important;
                  background: rgba(8,12,22,.72) !important;
                  white-space: pre-line !important;
                  text-align: left !important;
                  justify-content: flex-start !important;
                  align-items: flex-start !important;
                  padding: 10px !important;
                  line-height: 1.45 !important;
                  font-weight: 500 !important;
              }

              #calendar-page .cc-day-button button:hover {
                  background: rgba(139,92,246,.14) !important;
                  border-color: rgba(139,92,246,.68) !important;
              }


              #calendar-page .cc-calendar-dataframe {
                  overflow: hidden;
                  padding: 0 !important;
              }

              #calendar-page .cc-calendar-dataframe table {
                  width: 100% !important;
                  table-layout: fixed !important;
              }

              #calendar-page .cc-calendar-dataframe th {
                  text-align: center !important;
                  font-size: 12px !important;
                  font-weight: 700 !important;
                  opacity: .78;
              }

              #calendar-page .cc-calendar-dataframe td {
                  height: 105px !important;
                  vertical-align: top !important;
                  white-space: pre-line !important;
                  cursor: pointer !important;
                  background: rgba(8,12,22,.72) !important;
                  border: 1px solid rgba(148,163,184,.22) !important;
                  padding: 10px !important;
              }

              #calendar-page .cc-calendar-dataframe td:hover {
                  background: rgba(139,92,246,.14) !important;
                  border-color: rgba(139,92,246,.68) !important;
              }

              #calendar-page .cc-selected-day {
                  margin-top: 14px;
              }

              #calendar-page .cc-month-grid {
                  overflow: hidden;
                  padding: 0;
              }

              #calendar-page .cc-open-day-view {
                  min-height: 560px;
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

              #calendar-page .cc-day-empty {
                  opacity: .72;
                  padding: 18px 4px;
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

              #calendar-page .cc-open-day-event span {
                  opacity: .72;
              }

              @media (max-width: 760px) {
                  #calendar-page .cc-day-button button {
                      min-height: 82px !important;
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
            calendar_prev_button = gr.Button(
                "←",
                elem_classes=["cc-nav-button"],
            )
            calendar_today_button = gr.Button(
                "Today",
                elem_classes=["cc-today-button"],
            )
            calendar_next_button = gr.Button(
                "→",
                elem_classes=["cc-nav-button"],
            )

            month_heading = gr.Markdown(
                _month_heading(today.month, today.year),
                elem_classes=["cc-month-heading"],
            )

            calendar_status_filter = gr.Dropdown(
                ["All"] + CONTENT_STATUSES,
                value="All",
                label="Status",
                elem_classes=["cc-cyber-field"],
                scale=1,
            )

            calendar_type_filter = gr.Dropdown(
                ["All"] + CONTENT_TYPES,
                value="All",
                label="Type",
                elem_classes=["cc-cyber-field"],
                scale=1,
            )

        # One native Gradio calendar grid with one select callback.
        calendar_grid = gr.Dataframe(
            value=_calendar_matrix(
                "main",
                today.month,
                today.year,
                "All",
                "All",
            ),
            headers=[
                "SUN", "MON", "TUE", "WED",
                "THU", "FRI", "SAT",
            ],
            datatype=["str"] * 7,
            row_count=6,
            column_count=7,
            type="array",
            interactive=False,
            wrap=True,
            show_label=False,
            elem_classes=["cc-card", "cc-calendar-dataframe"],
        )

        # Hidden compatibility output used by the existing CRUD callbacks.
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

        with gr.Column(elem_classes=["cc-card", "cc-selected-day"]):
            day_view_heading = gr.Markdown("### Select a day")
            day_details_output = gr.HTML(
                '<div class="cc-day-empty">'
                'Click any date in the calendar to open it.'
                '</div>'
            )

        gr.Markdown(
            "### Content tools\n"
            "Add something new, update an existing item, "
            "or let Channel Coach plan your week."
        )

        with gr.Row(equal_height=False):
            with gr.Column(
                scale=1,
                min_width=300,
                elem_classes=["cc-card"],
            ):
                gr.Markdown("### ➕ Add Content")

                calendar_title = gr.Textbox(
                    label="Title",
                    placeholder="Example: Getting the Ice Rod",
                    elem_classes=["cc-cyber-field"],
                )

                calendar_content_type = gr.Dropdown(
                    CONTENT_TYPES,
                    value="Long Video",
                    label="Content Type",
                    elem_classes=["cc-cyber-field"],
                )

                calendar_game_topic = gr.Textbox(
                    label="Game / Topic",
                    placeholder="Example: Zelda ALTTP",
                    elem_classes=["cc-cyber-field"],
                )

                calendar_status = gr.Dropdown(
                    CONTENT_STATUSES,
                    value="Idea",
                    label="Status",
                    elem_classes=["cc-cyber-field"],
                )

                calendar_publish_date = gr.Textbox(
                    label="Target Publish Date",
                    value=today.isoformat(),
                    placeholder="YYYY-MM-DD",
                    elem_classes=["cc-cyber-field"],
                )

                calendar_notes = gr.Textbox(
                    label="Notes",
                    lines=4,
                    placeholder=(
                        "Example: Need thumbnail, voiceover, "
                        "and final export."
                    ),
                    elem_classes=["cc-cyber-field"],
                )

                calendar_add_button = gr.Button(
                    "➕ Add to Calendar"
                )

                calendar_message = gr.Textbox(
                    show_label=False,
                    placeholder="Calendar status",
                    lines=2,
                    elem_classes=["cc-cyber-field"],
                )

            with gr.Column(
                scale=1,
                min_width=300,
                elem_classes=["cc-card"],
            ):
                gr.Markdown("### 🔥 Coming Up")

                upcoming_output = gr.HTML(
                    value=render_upcoming_content(
                        user_id="main"
                    )
                )

                plan_week_button = gr.Button(
                    "✨ Plan My Week"
                )

                plan_week_output = gr.Textbox(
                    show_label=False,
                    placeholder="Weekly content plan",
                    lines=12,
                    elem_classes=["cc-cyber-field"],
                )

        gr.Markdown("### ✏️ Edit or Delete Content")

        with gr.Column(elem_classes=["cc-card"]):
            calendar_item_picker = gr.Dropdown(
                choices=get_calendar_choices("main"),
                label="Choose Calendar Item",
                elem_classes=["cc-cyber-field"],
            )

            calendar_load_button = gr.Button(
                "📂 Load Selected Item"
            )

            with gr.Row():
                calendar_update_button = gr.Button(
                    "💾 Save Edit"
                )
                calendar_delete_button = gr.Button(
                    "🗑️ Delete Selected Item"
                )

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
            upcoming_output,
            calendar_grid,
        ]

        calendar_prev_button.click(
            _previous_month_native,
            inputs=refresh_inputs,
            outputs=nav_outputs,
        )

        calendar_next_button.click(
            _next_month_native,
            inputs=refresh_inputs,
            outputs=nav_outputs,
        )

        calendar_today_button.click(
            _today_month_native,
            inputs=[
                workspace_name,
                calendar_status_filter,
                calendar_type_filter,
            ],
            outputs=nav_outputs,
        )

        calendar_status_filter.change(
            _month_refresh,
            inputs=refresh_inputs,
            outputs=calendar_grid,
        )

        calendar_type_filter.change(
            _month_refresh,
            inputs=refresh_inputs,
            outputs=calendar_grid,
        )

        calendar_grid.select(
            _select_calendar_day,
            inputs=refresh_inputs,
            outputs=[
                day_view_heading,
                day_details_output,
                calendar_publish_date,
            ],
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
            inputs=[
                calendar_item_picker,
                workspace_name,
            ],
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

        for event in [
            add_event,
            update_event,
            delete_event,
        ]:
            event.then(
                _month_refresh,
                inputs=refresh_inputs,
                outputs=calendar_grid,
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


# Temporary compatibility alias.
build_calendar_tab = build_calendar_page








      
