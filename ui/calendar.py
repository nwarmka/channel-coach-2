# Channel Coach - Full Screen Interactive Content Calendar

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


def _filtered_items(workspace_name):
    return load_content_calendar(workspace_name)


def _calendar_labels(workspace_name, month, year):
    month = int(month)
    year = int(year)
    today = date.today()
    dates = _six_week_dates(month, year)
    items = _filtered_items(workspace_name)

    labels = []

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
            if len(title) > 26:
                title = title[:23] + "..."
            lines.append(title)

        if len(day_items) > 3:
            lines.append(f"+{len(day_items) - 3} more")

        labels.append("\n".join(lines))

    return labels


def _button_updates(workspace_name, month, year):
    return tuple(
        gr.update(value=label)
        for label in _calendar_labels(workspace_name, month, year)
    )


def _refresh_month(workspace_name, month, year):
    return _button_updates(workspace_name, month, year)


def _move_month(workspace_name, month, year, delta):
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
        *_button_updates(workspace_name, month, year),
    )


def _previous_month(workspace_name, month, year):
    return _move_month(workspace_name, month, year, -1)


def _next_month(workspace_name, month, year):
    return _move_month(workspace_name, month, year, 1)


def _today_month(workspace_name):
    today = date.today()

    return (
        today.month,
        today.year,
        _month_heading(today.month, today.year),
        *_button_updates(workspace_name, today.month, today.year),
    )


def _day_details_html(workspace_name, selected_iso):
    items = _filtered_items(workspace_name)

    day_items = [
        item for item in items
        if item.get("publish_date") == selected_iso
    ]

    parts = ['<div class="cc-day-view-list">']

    if not day_items:
        parts.append(
            '<div class="cc-day-empty">'
            'Nothing scheduled for this day yet.'
            '</div>'
        )
    else:
        for item in day_items:
            title = html.escape(item.get("title") or "Untitled")
            status = html.escape(item.get("status") or "Idea")
            content_type = html.escape(
                item.get("content_type") or "Long Video"
            )
            topic = html.escape(item.get("game_topic") or "")
            notes = html.escape(item.get("notes") or "")

            parts.append(
                '<div class="cc-open-day-event">'
                f'<strong>{title}</strong>'
                f'<span>{status} · {content_type}</span>'
                + (f'<span>{topic}</span>' if topic else "")
                + (f'<span>{notes}</span>' if notes else "")
                + '</div>'
            )

    parts.append("</div>")
    return "".join(parts)


def _select_calendar_day(cell_index, workspace_name, month, year):
    try:
        selected = _six_week_dates(month, year)[int(cell_index)]
    except (TypeError, ValueError, IndexError):
        return (
            "### Select a day",
            '<div class="cc-day-empty">Click any date in the calendar.</div>',
            "",
            gr.update(visible=True),
            gr.update(visible=False),
            "",
            "",
            gr.update(choices=[], value=None),
        )

    selected_iso = selected.isoformat()

    heading = (
        f"### {selected.strftime('%A, %B')} "
        f"{selected.day}, {selected.year}"
    )

    return (
        heading,
        _day_details_html(workspace_name, selected_iso),
        selected_iso,
        gr.update(visible=False),
        gr.update(visible=True),
        "",
        "",
        gr.update(
            choices=_day_delete_choices(workspace_name, selected_iso),
            value=None,
        ),
    )


def _day_delete_choices(workspace_name, selected_iso):
    """Return (label, id) choices for items scheduled on the selected day."""
    if not selected_iso:
        return []

    choices = []
    for item in _filtered_items(workspace_name):
        if item.get("publish_date") != selected_iso:
            continue

        item_id = item.get("id")
        if item_id is None:
            continue

        title = (item.get("title") or "Untitled").strip()
        content_type = (item.get("content_type") or "").strip()
        label = f"{title} · {content_type}" if content_type else title
        choices.append((label, str(item_id)))

    return choices



PROGRESS_CHOICES = [
    ("0% · Start", "Idea"),
    ("20% · Planned", "Script"),
    ("40% · Recorded", "Recording"),
    ("60% · Edited", "Editing"),
    ("80% · Packaged", "Thumbnail"),
    ("100% · Complete", "Scheduled"),
]


def _day_progress_choices(workspace_name, selected_iso):
    """Return existing items on this day for the progress editor."""
    if not selected_iso:
        return []
    choices = []
    for item in _filtered_items(workspace_name):
        if item.get("publish_date") != selected_iso:
            continue
        item_id = item.get("id")
        if item_id is None:
            continue
        title = (item.get("title") or "Untitled").strip()
        choices.append((title, str(item_id)))
    return choices


def _load_progress_status(selected_item_id, workspace_name):
    """Load the saved status for the selected existing calendar item."""
    if not selected_item_id:
        return gr.update(value="Idea"), ""
    for item in _filtered_items(workspace_name):
        if str(item.get("id")) == str(selected_item_id):
            status = (item.get("status") or "Idea").strip()
            valid = {value for _, value in PROGRESS_CHOICES}
            if status == "Published":
                status = "Scheduled"
            if status not in valid:
                status = "Idea"
            return gr.update(value=status), ""
    return gr.update(value="Idea"), "Could not find that scheduled item."


def _save_progress_status(selected_item_id, new_status, selected_date, workspace_name, month, year):
    """Persist progress by updating the existing calendar item's status."""
    if not selected_item_id:
        return (
            "Choose a scheduled item first.",
            _day_details_html(workspace_name, selected_date),
            *_button_updates(workspace_name, month, year),
        )

    target = None
    for item in _filtered_items(workspace_name):
        if str(item.get("id")) == str(selected_item_id):
            target = item
            break

    if target is None:
        return (
            "Could not find that scheduled item.",
            _day_details_html(workspace_name, selected_date),
            *_button_updates(workspace_name, month, year),
        )

    result = update_content_item(
        selected_item_id,
        target.get("title") or "Untitled",
        target.get("platform") or "YouTube",
        target.get("content_type") or "Long Video",
        new_status or "Idea",
        target.get("publish_date") or selected_date,
        target.get("publish_time") or "",
        target.get("priority") or "Medium",
        target.get("notes") or "",
        target.get("tags") or "",
        month,
        year,
        "All",
        "All",
        workspace_name,
    )

    message = "Progress saved."
    if isinstance(result, (tuple, list)) and len(result) > 3 and result[3]:
        message = result[3]

    return (
        message,
        _day_details_html(workspace_name, selected_date),
        *_button_updates(workspace_name, month, year),
    )


def _delete_day_item(
    selected_item_id,
    selected_date,
    workspace_name,
    month,
    year,
):
    """Delete an item from the open calendar day and refresh the visible calendar."""
    if not selected_date:
        return (
            "Choose a date first.",
            gr.update(choices=[], value=None),
            '<div class="cc-day-empty">Click a date in the calendar.</div>',
            *_button_updates(workspace_name, month, year),
        )

    if not selected_item_id:
        return (
            "Choose a scheduled item to delete first.",
            gr.update(
                choices=_day_delete_choices(workspace_name, selected_date),
                value=None,
            ),
            _day_details_html(workspace_name, selected_date),
            *_button_updates(workspace_name, month, year),
        )

    # features.delete_content_item performs the database deletion.
    result = delete_content_item(
        selected_item_id,
        workspace_name,
        month,
        year,
        "All",
        "All",
    )

    status_message = result[3] if len(result) > 3 else "Calendar item deleted."

    return (
        status_message,
        gr.update(
            choices=_day_delete_choices(workspace_name, selected_date),
            value=None,
        ),
        _day_details_html(workspace_name, selected_date),
        *_button_updates(workspace_name, month, year),
    )


def _save_day_item(
    title,
    content_type,
    game_topic,
    status,
    selected_date,
    notes,
    workspace_name,
    month,
    year,
):
    title = (title or "").strip()

    if not selected_date:
        return (
            "Choose a date first.",
            "",
            notes or "",
            '<div class="cc-day-empty">Click a date in the calendar.</div>',
            *_button_updates(workspace_name, month, year),
        )

    if not title:
        return (
            "Type what you need to do first.",
            title,
            notes or "",
            _day_details_html(workspace_name, selected_date),
            *_button_updates(workspace_name, month, year),
        )

    # Reuse Channel Coach's existing calendar persistence.
    add_content_item(
        title,
        content_type,
        game_topic,
        status,
        selected_date,
        notes,
        month,
        year,
        "All",
        "All",
        workspace_name,
    )

    return (
        f"Saved to {selected_date}.",
        "",
        "",
        _day_details_html(workspace_name, selected_date),
        *_button_updates(workspace_name, month, year),
    )


def _close_day():
    return (
        gr.update(visible=True),
        gr.update(visible=False),
    )


def _make_day_handler(cell_index):
    def open_day(workspace_name, month, year):
        return _select_calendar_day(
            cell_index,
            workspace_name,
            month,
            year,
        )

    return open_day



def _open_external_calendar_date(requested_date, workspace_name, current_month, current_year):
    """Open a specific YYYY-MM-DD from another Gradio component."""
    try:
        chosen = date.fromisoformat((requested_date or "").strip())
    except (TypeError, ValueError):
        return (
            current_month, current_year, _month_heading(current_month, current_year),
            *_button_updates(workspace_name, current_month, current_year),
            "### Select a day",
            '<div class="cc-day-empty">Choose a valid calendar date.</div>',
            "", gr.update(visible=True), gr.update(visible=False),
            "", "", gr.update(choices=[], value=None),
        )

    month, year = chosen.month, chosen.year
    selected = chosen.isoformat()
    return (
        month, year, _month_heading(month, year),
        *_button_updates(workspace_name, month, year),
        f"### {chosen.strftime('%A, %B %d, %Y')}",
        _day_details_html(workspace_name, selected),
        selected,
        gr.update(visible=False),
        gr.update(visible=True),
        "",
        "",
        gr.update(choices=_day_delete_choices(workspace_name, selected), value=None),
    )

def build_calendar_page(workspace_name, visible=False):
    today = date.today()

    with gr.Column(
        visible=visible,
        elem_id="calendar-page",
    ) as calendar_page:

        gr.HTML(
            """
            <style>
            #calendar-page {
                width: 100% !important;
                max-width: none !important;
                margin: 0 !important;
                padding: 0 10px 24px !important;
            }

            #calendar-page .cc-calendar-header {
                margin: 2px 0 8px;
            }

            #calendar-page .cc-calendar-kicker {
                color: #16d9ff;
                font-size: .70rem;
                font-weight: 800;
                letter-spacing: .16em;
                text-transform: uppercase;
                margin-bottom: 2px;
            }

            #calendar-page .cc-calendar-title {
                margin: 0;
                font-size: 1.65rem;
                line-height: 1.1;
            }

            #calendar-page .cc-calendar-subtitle {
                opacity: .72;
                margin-top: 2px;
                font-size: .90rem;
                line-height: 1.2;
            }

            #calendar-page .cc-toolbar {
                padding: 4px 8px !important;
                margin-bottom: 6px !important;
                border-radius: 12px !important;
                min-height: 0 !important;
                flex-wrap: nowrap !important;
                align-items: center !important;
            }

            #calendar-page .cc-nav-row {
                align-items: center !important;
                gap: 5px !important;
                min-height: 0 !important;
                flex-wrap: nowrap !important;
            }

            #calendar-page .cc-nav-button {
                min-width: 42px !important;
                max-width: 46px !important;
                min-height: 34px !important;
                height: 34px !important;
                padding: 3px 8px !important;
            }

            #calendar-page .cc-today-button {
                min-width: 76px !important;
                max-width: 86px !important;
                min-height: 34px !important;
                height: 34px !important;
                padding: 3px 10px !important;
            }

            #calendar-page .cc-month-heading {
                flex: 1 1 auto !important;
                min-width: 0 !important;
                text-align: center;
            }

            #calendar-page .cc-month-heading h2 {
                margin: 0 !important;
                line-height: 1 !important;
                font-size: 1.20rem !important;
            }

            #calendar-page .cc-month-grid {
                width: 100% !important;
                overflow: hidden;
                padding: 0 !important;
                border-radius: 16px !important;
            }

            #calendar-page .cc-weekday-row,
            #calendar-page .cc-day-row {
                gap: 0 !important;
            }

            #calendar-page .cc-weekday-label {
                text-align: center;
                font-size: 12px;
                font-weight: 800;
                letter-spacing: .04em;
                opacity: .78;
                padding: 10px 0;
            }

            #calendar-page .cc-day-button {
                min-width: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                border: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
                pointer-events: auto !important;
                position: relative !important;
                z-index: 2 !important;
            }

            #calendar-page .cc-day-button button,
            #calendar-page button.cc-day-button {
                width: 100% !important;
                min-height: 132px !important;
                margin: 0 !important;
                border-radius: 0 !important;
                border: 1px solid rgba(148,163,184,.20) !important;
                background: rgba(7,10,17,.80) !important;
                white-space: pre-line !important;
                text-align: left !important;
                justify-content: flex-start !important;
                align-items: flex-start !important;
                padding: 11px !important;
                line-height: 1.45 !important;
                font-weight: 600 !important;
                cursor: pointer !important;
                pointer-events: auto !important;
            }

            #calendar-page .cc-day-button button:hover,
            #calendar-page button.cc-day-button:hover {
                background: rgba(139,92,246,.16) !important;
                border-color: rgba(255,62,165,.62) !important;
                transform: none !important;
            }

            #calendar-page .cc-open-day-view {
                width: 100% !important;
                min-height: 620px;
                padding: 18px !important;
            }

            #calendar-page .cc-day-back {
                max-width: 180px;
                margin-bottom: 12px;
            }

            #calendar-page .cc-day-form {
                margin: 10px 0 18px !important;
                padding: 16px !important;
                border: 1px solid rgba(255,62,165,.30) !important;
                border-radius: 14px !important;
                background: rgba(7,10,17,.72) !important;
            }

            #calendar-page .cc-save-day {
                margin-top: 8px !important;
            }

            #calendar-page .cc-day-view-list {
                display: flex;
                flex-direction: column;
                gap: 10px;
                margin-top: 14px;
            }

            #calendar-page .cc-day-empty {
                opacity: .72;
                padding: 22px 4px;
            }

            #calendar-page .cc-open-day-event {
                display: flex;
                flex-direction: column;
                gap: 5px;
                padding: 14px 16px;
                border-left: 4px solid #8b5cf6;
                border-radius: 10px;
                background: rgba(139,92,246,.10);
            }

            #calendar-page .cc-open-day-event span {
                opacity: .72;
            }

            #calendar-page .cc-delete-day-form {
                margin: 12px 0 18px !important;
                padding: 16px !important;
                border: 1px solid rgba(239,68,68,.42) !important;
                border-radius: 14px !important;
                background: rgba(127,29,29,.10) !important;
            }

            #calendar-page .cc-delete-day-button button,
            #calendar-page button.cc-delete-day-button {
                margin-top: 8px !important;
            }


            @media (max-width: 760px) {
                #calendar-page {
                    padding-left: 4px !important;
                    padding-right: 4px !important;
                }

                #calendar-page .cc-day-button button,
                #calendar-page button.cc-day-button {
                    min-height: 88px !important;
                    padding: 6px !important;
                    font-size: 12px !important;
                }

                #calendar-page .cc-calendar-title {
                    font-size: 1.40rem;
                }
            }
            /* Keep Calendar day cells above Gradio/global card styling */
            #calendar-page .cc-month-grid .cc-day-button {
                position: relative !important;
                z-index: 10 !important;
                pointer-events: auto !important;
            }

            #calendar-page .cc-month-grid .cc-day-button * {
                pointer-events: none !important;
            }

            #calendar-page .cc-month-grid button.cc-day-button {
                pointer-events: auto !important;
                cursor: pointer !important;
            }

            </style>

            <div class="cc-calendar-header">
                <div class="cc-calendar-kicker">Creator Planner</div>
                <h2 class="cc-calendar-title">📅 Content Calendar</h2>
                <div class="cc-calendar-subtitle">
                    Click a date to plan that day.
                </div>
            </div>
            """
        )

        calendar_month = gr.State(today.month)
        calendar_year = gr.State(today.year)

        with gr.Row(elem_classes=["cc-toolbar", "cc-nav-row"]):
            prev_button = gr.Button(
                "←",
                elem_classes=["cc-nav-button"],
            )

            today_button = gr.Button(
                "Today",
                elem_classes=["cc-today-button"],
            )

            month_heading = gr.Markdown(
                _month_heading(today.month, today.year),
                elem_classes=["cc-month-heading"],
            )

            next_button = gr.Button(
                "→",
                elem_classes=["cc-nav-button"],
            )

        initial_labels = _calendar_labels(
            "main",
            today.month,
            today.year,
        )

        with gr.Column(
            elem_classes=["cc-month-grid"],
            visible=True,
        ) as month_grid_container:

            with gr.Row(elem_classes=["cc-weekday-row"]):
                for weekday in [
                    "SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"
                ]:
                    gr.Markdown(
                        weekday,
                        elem_classes=["cc-weekday-label"],
                        min_width=0,
                    )

            calendar_day_buttons = []

            for week_index in range(6):
                with gr.Row(elem_classes=["cc-day-row"]):
                    for day_index in range(7):
                        cell_index = week_index * 7 + day_index

                        button = gr.Button(
                            initial_labels[cell_index],
                            elem_classes=["cc-day-button"],
                            min_width=0,
                            scale=1,
                        )
                        calendar_day_buttons.append(button)

        selected_date = gr.Textbox(visible=False)

        # Dedicated server-side bridge for opening a calendar date from Home/Dashboard.
        # Keeping this separate from selected_date prevents a .change() event from
        # writing back to the same component that triggered it.
        calendar_open_request = gr.Textbox(
            value="",
            visible=False,
            elem_id="calendar-open-request",
        )

        with gr.Column(
            elem_classes=["cc-open-day-view"],
            visible=False,
        ) as selected_day_container:
            back_button = gr.Button(
                "← Back to Month",
                elem_classes=["cc-day-back"],
            )

            day_view_heading = gr.Markdown("### Select a day")

            with gr.Column(elem_classes=["cc-day-form"]):
                task_title = gr.Textbox(
                    label="What do you need to do?",
                    placeholder="Example: Edit Walking Dead Short",
                )

                with gr.Row():
                    task_content_type = gr.Dropdown(
                        CONTENT_TYPES,
                        value=CONTENT_TYPES[0] if CONTENT_TYPES else None,
                        label="Content Type",
                    )

                    task_status = gr.Dropdown(
                        CONTENT_STATUSES,
                        value=CONTENT_STATUSES[0] if CONTENT_STATUSES else None,
                        label="Status",
                    )

                task_game_topic = gr.Textbox(
                    label="Game / Topic",
                    placeholder="Optional",
                )

                task_notes = gr.Textbox(
                    label="Notes",
                    placeholder="Anything else you need to remember...",
                    lines=3,
                )

                save_day_button = gr.Button(
                    "💾 Save to This Day",
                    variant="primary",
                    elem_classes=["cc-save-day"],
                )

                save_day_status = gr.Markdown()

            gr.Markdown("### Scheduled for this day")
            day_details_output = gr.HTML(
                '<div class="cc-day-empty">'
                'Nothing scheduled for this day yet.'
                '</div>'
            )

            with gr.Column(elem_classes=["cc-day-form"]):
                gr.Markdown("### 📈 Project Progress")

                progress_item_picker = gr.Dropdown(
                    choices=[],
                    label="Choose a scheduled item",
                    value=None,
                )

                progress_stage = gr.Dropdown(
                    choices=PROGRESS_CHOICES,
                    value="Idea",
                    label="Project stage",
                    info="Choose how far along this project is.",
                    elem_classes=["cc-progress-stage"],
                )

                gr.HTML(
                    """
                    <div style="opacity:.78;font-size:.88rem;line-height:1.5;margin:-2px 0 10px;">
                        Start 0% → Planned 20% → Recorded 40% → Edited 60% →
                        Packaged 80% → Complete 100%
                    </div>
                    """
                )

                save_progress_button = gr.Button(
                    "💾 Save Progress",
                    variant="primary",
                )

                progress_status = gr.Markdown()

            with gr.Column(elem_classes=["cc-delete-day-form"]):
                gr.Markdown("### 🗑️ Delete a scheduled item")

                delete_day_picker = gr.Dropdown(
                    choices=[],
                    label="Choose an item from this day",
                    value=None,
                )

                delete_day_button = gr.Button(
                    "🗑️ Delete Selected Item",
                    variant="stop",
                    elem_classes=["cc-delete-day-button"],
                )

                delete_day_status = gr.Markdown()

        # Hidden compatibility components expected by app.py.
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

        upcoming_output = gr.HTML(
            value=render_upcoming_content(user_id="main"),
            visible=False,
        )

        calendar_item_picker = gr.Dropdown(
            choices=get_calendar_choices("main"),
            visible=False,
        )

        refresh_inputs = [
            workspace_name,
            calendar_month,
            calendar_year,
        ]

        nav_outputs = [
            calendar_month,
            calendar_year,
            month_heading,
            *calendar_day_buttons,
        ]

        prev_button.click(
            _previous_month,
            inputs=refresh_inputs,
            outputs=nav_outputs,
            show_progress="hidden",
        )

        next_button.click(
            _next_month,
            inputs=refresh_inputs,
            outputs=nav_outputs,
            show_progress="hidden",
        )

        today_button.click(
            _today_month,
            inputs=[workspace_name],
            outputs=nav_outputs,
            show_progress="hidden",
        )

        workspace_name.change(
            _refresh_month,
            inputs=refresh_inputs,
            outputs=calendar_day_buttons,
            show_progress="hidden",
        )

        for cell_index, day_button in enumerate(calendar_day_buttons):
            day_button.click(
                fn=_make_day_handler(cell_index),
                inputs=refresh_inputs,
                outputs=[
                    day_view_heading,
                    day_details_output,
                    selected_date,
                    month_grid_container,
                    selected_day_container,
                    save_day_status,
                    task_title,
                    delete_day_picker,
                ],
                show_progress="hidden",
            )

        calendar_open_request.change(
            _open_external_calendar_date,
            inputs=[calendar_open_request, workspace_name, calendar_month, calendar_year],
            outputs=[
                calendar_month, calendar_year, month_heading,
                *calendar_day_buttons,
                day_view_heading, day_details_output, selected_date,
                month_grid_container, selected_day_container,
                save_day_status, task_title, delete_day_picker,
            ],
            show_progress="hidden",
        )

        save_day_button.click(
            _save_day_item,
            inputs=[
                task_title,
                task_content_type,
                task_game_topic,
                task_status,
                selected_date,
                task_notes,
                workspace_name,
                calendar_month,
                calendar_year,
            ],
            outputs=[
                save_day_status,
                task_title,
                task_notes,
                day_details_output,
                *calendar_day_buttons,
            ],
            show_progress="hidden",
        )

        # Populate Project Progress whenever a calendar day is opened.
        for cell_index, day_button in enumerate(calendar_day_buttons):
            day_button.click(
                lambda workspace, month, year, idx=cell_index: gr.update(
                    choices=_day_progress_choices(
                        workspace,
                        _six_week_dates(month, year)[int(idx)].isoformat(),
                    ),
                    value=None,
                ),
                inputs=refresh_inputs,
                outputs=[progress_item_picker],
                show_progress="hidden",
            )

        calendar_open_request.change(
            lambda requested, workspace: gr.update(
                choices=_day_progress_choices(workspace, (requested or "").strip()),
                value=None,
            ),
            inputs=[calendar_open_request, workspace_name],
            outputs=[progress_item_picker],
            show_progress="hidden",
        )

        progress_item_picker.change(
            _load_progress_status,
            inputs=[progress_item_picker, workspace_name],
            outputs=[progress_stage, progress_status],
            show_progress="hidden",
        )

        save_progress_button.click(
            _save_progress_status,
            inputs=[
                progress_item_picker,
                progress_stage,
                selected_date,
                workspace_name,
                calendar_month,
                calendar_year,
            ],
            outputs=[
                progress_status,
                day_details_output,
                *calendar_day_buttons,
            ],
            show_progress="hidden",
        )

        delete_day_button.click(
            _delete_day_item,
            inputs=[
                delete_day_picker,
                selected_date,
                workspace_name,
                calendar_month,
                calendar_year,
            ],
            outputs=[
                delete_day_status,
                delete_day_picker,
                day_details_output,
                *calendar_day_buttons,
            ],
            show_progress="hidden",
        )

        back_button.click(
            _close_day,
            inputs=None,
            outputs=[
                month_grid_container,
                selected_day_container,
            ],
            show_progress="hidden",
        )

    return (
        calendar_page,
        calendar_output,
        upcoming_output,
        calendar_item_picker,
        calendar_open_request,
    )


build_calendar_tab = build_calendar_page
















      






      







      
