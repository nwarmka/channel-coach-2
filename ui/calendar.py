# Channel Coach - Full Screen Content Calendar UI

import calendar as pycalendar
import html
from datetime import date, timedelta

import gradio as gr

from features import (
    get_calendar_choices,
    load_content_calendar,
    render_content_calendar,
    render_upcoming_content,
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


def _select_calendar_day(cell_index, workspace_name, month, year):
    try:
        selected = _six_week_dates(month, year)[int(cell_index)]
    except (TypeError, ValueError, IndexError):
        return (
            "### Select a day",
            '<div class="cc-day-empty">Click any date in the calendar.</div>',
            gr.update(visible=True),
            gr.update(visible=False),
        )

    items = _filtered_items(workspace_name)
    day_items = [
        item for item in items
        if item.get("publish_date") == selected.isoformat()
    ]

    heading = (
        f"### {selected.strftime('%A, %B')} "
        f"{selected.day}, {selected.year}"
    )

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

            parts.append(
                '<div class="cc-open-day-event">'
                f'<strong>{title}</strong>'
                f'<span>{status} · {content_type}</span>'
                + (f'<span>{topic}</span>' if topic else "")
                + '</div>'
            )

    parts.append("</div>")

    return (
        heading,
        "".join(parts),
        gr.update(visible=False),
        gr.update(visible=True),
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
                margin: 4px 0 14px;
            }

            #calendar-page .cc-calendar-kicker {
                color: #16d9ff;
                font-size: .76rem;
                font-weight: 800;
                letter-spacing: .16em;
                text-transform: uppercase;
                margin-bottom: 4px;
            }

            #calendar-page .cc-calendar-title {
                margin: 0;
                font-size: 2rem;
            }

            #calendar-page .cc-calendar-subtitle {
                opacity: .72;
                margin-top: 4px;
            }

            #calendar-page .cc-toolbar {
                padding: 10px 12px !important;
                margin-bottom: 10px !important;
                border-radius: 14px !important;
            }

            #calendar-page .cc-nav-row {
                align-items: center;
                gap: 8px;
            }

            #calendar-page .cc-nav-button {
                min-width: 48px !important;
                max-width: 56px !important;
            }

            #calendar-page .cc-today-button {
                min-width: 88px !important;
                max-width: 110px !important;
            }

            #calendar-page .cc-month-heading {
                flex: 1 1 auto;
                text-align: center;
            }

            #calendar-page .cc-month-heading h2 {
                margin: 0 !important;
                line-height: 1.15 !important;
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
                    font-size: 1.55rem;
                }
            }
            </style>

            <div class="cc-calendar-header">
                <div class="cc-calendar-kicker">Creator Planner</div>
                <h2 class="cc-calendar-title">📅 Content Calendar</h2>
                <div class="cc-calendar-subtitle">
                    Click a date to open that day.
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

        with gr.Column(
            elem_classes=["cc-open-day-view"],
            visible=False,
        ) as selected_day_container:
            back_button = gr.Button(
                "← Back to Month",
                elem_classes=["cc-day-back"],
            )

            day_view_heading = gr.Markdown("### Select a day")
            day_details_output = gr.HTML(
                '<div class="cc-day-empty">'
                'Click a date in the calendar.'
                '</div>'
            )

        # Keep these hidden because app.py expects them.
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
                    month_grid_container,
                    selected_day_container,
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
    )


build_calendar_tab = build_calendar_page







      






      







      
