# Channel Coach main app
# UI lives here. Feature functions, styles, constants, and helpers are imported from features.py.

from features import *

with gr.Blocks(title="Channel Coach", head=custom_head, css=custom_css) as app:

    gr.HTML(
        f"""
        <div class="cc-logo-float">
            <img
                src="data:image/png;base64,{CHANNEL_COACH_LOGO_BASE64}"
                alt="Channel Coach Logo"
                class="cc-header-logo"
                style="width:250px !important; max-width:250px !important; min-width:250px !important; height:auto !important;"
            >
        </div>
        """,
        elem_id="cc-logo-header-block",
        container=False,
        padding=False,
        min_height=0
    )

    saved_profile = load_creator_profile()

    with gr.Tab("🏠 Dashboard"):
        gr.Markdown("## 🕹️ Creator Dashboard\n\nYour home base for upcoming content, overdue projects, and quick AI guidance.")
        dashboard_output = gr.HTML(value=render_creator_dashboard())

        with gr.Row():
            dashboard_refresh_button = gr.Button("🔄 Refresh Dashboard")
            dashboard_tip_button = gr.Button("✨ Give Me One AI Tip")

        dashboard_tip_output = gr.Textbox(label="AI Dashboard Tip", lines=5)

        dashboard_refresh_button.click(
            refresh_creator_dashboard,
            inputs=[],
            outputs=dashboard_output
        )

        dashboard_tip_button.click(
            dashboard_ai_tip,
            inputs=[],
            outputs=dashboard_tip_output,
            show_progress="full"
        )



    with gr.Tab("📅 Content Calendar"):
        gr.Markdown(
            """
            ## 📅 Content Calendar
            Plan your long videos, Shorts, Reels, TikToks, livestreams, and community posts.

            Date format: **YYYY-MM-DD**. Example: **2026-06-28**
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                cc_calendar_title = gr.Textbox(
                    label="Title",
                    placeholder="Example: Getting the Ice Rod"
                )
                cc_calendar_content_type = gr.Dropdown(
                    CONTENT_TYPES,
                    value="Long Video",
                    label="Content Type"
                )
                cc_calendar_game_topic = gr.Textbox(
                    label="Game / Topic",
                    placeholder="Example: Zelda ALTTP"
                )
                cc_calendar_status = gr.Dropdown(
                    CONTENT_STATUSES,
                    value="Idea",
                    label="Status"
                )
                cc_calendar_publish_date = gr.Textbox(
                    label="Target Publish Date",
                    value=date.today().isoformat(),
                    placeholder="YYYY-MM-DD"
                )
                cc_calendar_notes = gr.Textbox(
                    label="Notes",
                    lines=4,
                    placeholder="Example: Need thumbnail, voiceover, and final export."
                )

                cc_calendar_add_button = gr.Button("➕ Add to Calendar")
                cc_calendar_message = gr.Textbox(label="Calendar Status", lines=2)

                cc_upcoming_output = gr.HTML(value=render_upcoming_content())

                cc_plan_week_button = gr.Button("✨ Plan My Week")
                cc_plan_week_output = gr.Textbox(label="AI Weekly Plan", lines=12)

            with gr.Column(scale=2):
                with gr.Row():
                    cc_calendar_month = gr.Dropdown(
                        choices=list(range(1, 13)),
                        value=date.today().month,
                        label="Month"
                    )
                    cc_calendar_year = gr.Number(
                        value=date.today().year,
                        label="Year",
                        precision=0
                    )

                with gr.Row():
                    cc_calendar_status_filter = gr.Dropdown(
                        ["All"] + CONTENT_STATUSES,
                        value="All",
                        label="Status Filter"
                    )
                    cc_calendar_type_filter = gr.Dropdown(
                        ["All"] + CONTENT_TYPES,
                        value="All",
                        label="Type Filter"
                    )

                cc_calendar_output = gr.HTML(value=render_content_calendar())
                cc_calendar_refresh_button = gr.Button("🔄 Refresh Calendar")

        gr.Markdown("### Edit or Delete Calendar Item")

        cc_calendar_item_picker = gr.Dropdown(
            choices=get_calendar_choices(),
            label="Choose Calendar Item"
        )

        cc_calendar_load_button = gr.Button("📂 Load Selected Item")

        with gr.Row():
            cc_calendar_update_button = gr.Button("💾 Save Edit")
            cc_calendar_delete_button = gr.Button("🗑️ Delete Selected Item")

        cc_calendar_add_button.click(
            add_content_item,
            inputs=[
                cc_calendar_title,
                cc_calendar_content_type,
                cc_calendar_game_topic,
                cc_calendar_status,
                cc_calendar_publish_date,
                cc_calendar_notes,
                cc_calendar_month,
                cc_calendar_year,
                cc_calendar_status_filter,
                cc_calendar_type_filter
            ],
            outputs=[cc_calendar_output, cc_upcoming_output, cc_calendar_item_picker, cc_calendar_message]
        )

        cc_calendar_refresh_button.click(
            refresh_content_calendar,
            inputs=[cc_calendar_month, cc_calendar_year, cc_calendar_status_filter, cc_calendar_type_filter],
            outputs=[cc_calendar_output, cc_upcoming_output]
        )

        cc_calendar_month.change(
            refresh_content_calendar,
            inputs=[cc_calendar_month, cc_calendar_year, cc_calendar_status_filter, cc_calendar_type_filter],
            outputs=[cc_calendar_output, cc_upcoming_output]
        )

        cc_calendar_year.change(
            refresh_content_calendar,
            inputs=[cc_calendar_month, cc_calendar_year, cc_calendar_status_filter, cc_calendar_type_filter],
            outputs=[cc_calendar_output, cc_upcoming_output]
        )

        cc_calendar_status_filter.change(
            refresh_content_calendar,
            inputs=[cc_calendar_month, cc_calendar_year, cc_calendar_status_filter, cc_calendar_type_filter],
            outputs=[cc_calendar_output, cc_upcoming_output]
        )

        cc_calendar_type_filter.change(
            refresh_content_calendar,
            inputs=[cc_calendar_month, cc_calendar_year, cc_calendar_status_filter, cc_calendar_type_filter],
            outputs=[cc_calendar_output, cc_upcoming_output]
        )

        cc_calendar_load_button.click(
            load_selected_content_item,
            inputs=cc_calendar_item_picker,
            outputs=[
                cc_calendar_title,
                cc_calendar_content_type,
                cc_calendar_game_topic,
                cc_calendar_status,
                cc_calendar_publish_date,
                cc_calendar_notes,
                cc_calendar_message
            ]
        )

        cc_calendar_update_button.click(
            update_content_item,
            inputs=[
                cc_calendar_item_picker,
                cc_calendar_title,
                cc_calendar_content_type,
                cc_calendar_game_topic,
                cc_calendar_status,
                cc_calendar_publish_date,
                cc_calendar_notes,
                cc_calendar_month,
                cc_calendar_year,
                cc_calendar_status_filter,
                cc_calendar_type_filter
            ],
            outputs=[cc_calendar_output, cc_upcoming_output, cc_calendar_item_picker, cc_calendar_message]
        )

        cc_calendar_delete_button.click(
            delete_content_item,
            inputs=[
                cc_calendar_item_picker,
                cc_calendar_month,
                cc_calendar_year,
                cc_calendar_status_filter,
                cc_calendar_type_filter
            ],
            outputs=[cc_calendar_output, cc_upcoming_output, cc_calendar_item_picker, cc_calendar_message]
        )

        cc_plan_week_button.click(
            plan_my_week,
            inputs=[],
            outputs=cc_plan_week_output,
            show_progress="full"
        )



    with gr.Tab("📁 Projects"):
        gr.Markdown("## 📁 Projects\n\nPlan your content, manage production, and open full workspaces for each video or Short.")

        with gr.Accordion("📅 Content Calendar", open=True):
            gr.Markdown(
                """
                ## 📅 Content Calendar
                Plan your long videos, Shorts, livestreams, and community posts.

                Date format: **YYYY-MM-DD**. Example: **2026-06-28**
                """
            )

            with gr.Row():
                with gr.Column(scale=1):
                    calendar_title = gr.Textbox(
                        label="Title",
                        placeholder="Example: Getting the Ice Rod"
                    )
                    calendar_content_type = gr.Dropdown(
                        CONTENT_TYPES,
                        value="Long Video",
                        label="Content Type"
                    )
                    calendar_game_topic = gr.Textbox(
                        label="Game / Topic",
                        placeholder="Example: Zelda ALTTP"
                    )
                    calendar_status = gr.Dropdown(
                        CONTENT_STATUSES,
                        value="Idea",
                        label="Status"
                    )
                    calendar_publish_date = gr.Textbox(
                        label="Target Publish Date",
                        value=date.today().isoformat(),
                        placeholder="YYYY-MM-DD"
                    )
                    calendar_notes = gr.Textbox(
                        label="Notes",
                        lines=4,
                        placeholder="Example: Need thumbnail, voiceover, and final export."
                    )

                    calendar_add_button = gr.Button("➕ Add to Calendar")
                    calendar_message = gr.Textbox(label="Calendar Status", lines=2)

                    upcoming_output = gr.HTML(value=render_upcoming_content())

                    plan_week_button = gr.Button("✨ Plan My Week")
                    plan_week_output = gr.Textbox(label="AI Weekly Plan", lines=12)

                with gr.Column(scale=2):
                    with gr.Row():
                        calendar_month = gr.Dropdown(
                            choices=list(range(1, 13)),
                            value=date.today().month,
                            label="Month"
                        )
                        calendar_year = gr.Number(
                            value=date.today().year,
                            label="Year",
                            precision=0
                        )

                    with gr.Row():
                        calendar_status_filter = gr.Dropdown(
                            ["All"] + CONTENT_STATUSES,
                            value="All",
                            label="Status Filter"
                        )
                        calendar_type_filter = gr.Dropdown(
                            ["All"] + CONTENT_TYPES,
                            value="All",
                            label="Type Filter"
                        )

                    calendar_output = gr.HTML(value=render_content_calendar())
                    calendar_refresh_button = gr.Button("🔄 Refresh Calendar")

            gr.Markdown("### Edit or Delete Calendar Item")

            calendar_item_picker = gr.Dropdown(
                choices=get_calendar_choices(),
                label="Choose Calendar Item"
            )

            calendar_load_button = gr.Button("📂 Load Selected Item")

            with gr.Row():
                calendar_update_button = gr.Button("💾 Save Edit")
                calendar_delete_button = gr.Button("🗑️ Delete Selected Item")

            calendar_add_button.click(
                add_content_item,
                inputs=[
                    calendar_title,
                    calendar_content_type,
                    calendar_game_topic,
                    calendar_status,
                    calendar_publish_date,
                    calendar_notes,
                    calendar_month,
                    calendar_year,
                    calendar_status_filter,
                    calendar_type_filter
                ],
                outputs=[calendar_output, upcoming_output, calendar_item_picker, calendar_message]
            )

            calendar_refresh_button.click(
                refresh_content_calendar,
                inputs=[calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
                outputs=[calendar_output, upcoming_output]
            )

            calendar_month.change(
                refresh_content_calendar,
                inputs=[calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
                outputs=[calendar_output, upcoming_output]
            )

            calendar_year.change(
                refresh_content_calendar,
                inputs=[calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
                outputs=[calendar_output, upcoming_output]
            )

            calendar_status_filter.change(
                refresh_content_calendar,
                inputs=[calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
                outputs=[calendar_output, upcoming_output]
            )

            calendar_type_filter.change(
                refresh_content_calendar,
                inputs=[calendar_month, calendar_year, calendar_status_filter, calendar_type_filter],
                outputs=[calendar_output, upcoming_output]
            )

            calendar_load_button.click(
                load_selected_content_item,
                inputs=calendar_item_picker,
                outputs=[
                    calendar_title,
                    calendar_content_type,
                    calendar_game_topic,
                    calendar_status,
                    calendar_publish_date,
                    calendar_notes,
                    calendar_message
                ]
            )

            calendar_update_button.click(
                update_content_item,
                inputs=[
                    calendar_item_picker,
                    calendar_title,
                    calendar_content_type,
                    calendar_game_topic,
                    calendar_status,
                    calendar_publish_date,
                    calendar_notes,
                    calendar_month,
                    calendar_year,
                    calendar_status_filter,
                    calendar_type_filter
                ],
                outputs=[calendar_output, upcoming_output, calendar_item_picker, calendar_message]
            )

            calendar_delete_button.click(
                delete_content_item,
                inputs=[
                    calendar_item_picker,
                    calendar_month,
                    calendar_year,
                    calendar_status_filter,
                    calendar_type_filter
                ],
                outputs=[calendar_output, upcoming_output, calendar_item_picker, calendar_message]
            )

            plan_week_button.click(
                plan_my_week,
                inputs=[],
                outputs=plan_week_output,
                show_progress="full"
            )



        with gr.Accordion("🎬 Project Workspace", open=False):
            gr.Markdown(
                """
                ## 🎬 Project Workspace
                Open any calendar item as a full creator project. Track real checklist progress, save notes, and generate project-specific AI help.
                """
            )

            workspace_project_picker = gr.Dropdown(
                choices=get_calendar_choices(),
                label="Choose Project"
            )
            workspace_load_button = gr.Button("📂 Load Project")
            workspace_overview = gr.HTML(value=render_project_workspace_overview(None))

            with gr.Row():
                with gr.Column(scale=1):
                    workspace_title = gr.Textbox(label="Project Title")
                    workspace_content_type = gr.Dropdown(CONTENT_TYPES, value="Long Video", label="Content Type")
                    workspace_game_topic = gr.Textbox(label="Game / Topic")
                    workspace_status = gr.Dropdown(CONTENT_STATUSES, value="Idea", label="Status")
                    workspace_publish_date = gr.Textbox(label="Target Publish Date", value=date.today().isoformat())

                    gr.Markdown("### Production Checklist")
                    workspace_script_written = gr.Checkbox(label="Script written")
                    workspace_gameplay_recorded = gr.Checkbox(label="Gameplay recorded")
                    workspace_voiceover_recorded = gr.Checkbox(label="Voiceover recorded")
                    workspace_editing_complete = gr.Checkbox(label="Editing complete")
                    workspace_thumbnail_finished = gr.Checkbox(label="Thumbnail finished")
                    workspace_description_done = gr.Checkbox(label="Description done")
                    workspace_uploaded_scheduled = gr.Checkbox(label="Uploaded / scheduled")
                    workspace_shared_social = gr.Checkbox(label="Shared on social media")

                    workspace_save_button = gr.Button("💾 Save Project Workspace")
                    workspace_message = gr.Textbox(label="Workspace Status", lines=2)

                with gr.Column(scale=2):
                    workspace_project_notes = gr.Textbox(label="Project Notes", lines=6)
                    workspace_description_draft = gr.Textbox(label="Description Draft", lines=7)
                    workspace_thumbnail_notes = gr.Textbox(label="Thumbnail Notes", lines=5)
                    workspace_shorts_ideas_draft = gr.Textbox(label="Shorts Ideas / Clip Notes", lines=5)

                    gr.Markdown("### AI Project Assistant")
                    with gr.Row():
                        workspace_titles_button = gr.Button("✨ Generate Titles")
                        workspace_description_button = gr.Button("📝 Generate Description")
                        workspace_thumbnail_button = gr.Button("🖼 Thumbnail Ideas")

                    with gr.Row():
                        workspace_shorts_button = gr.Button("📱 Shorts Ideas")
                        workspace_review_button = gr.Button("🎬 Project Review")

                    workspace_ai_output = gr.Textbox(label="AI Project Output", lines=14)

            workspace_load_button.click(
                load_project_workspace,
                inputs=workspace_project_picker,
                outputs=[
                    workspace_overview,
                    workspace_title,
                    workspace_content_type,
                    workspace_game_topic,
                    workspace_status,
                    workspace_publish_date,
                    workspace_project_notes,
                    workspace_script_written,
                    workspace_gameplay_recorded,
                    workspace_voiceover_recorded,
                    workspace_editing_complete,
                    workspace_thumbnail_finished,
                    workspace_description_done,
                    workspace_uploaded_scheduled,
                    workspace_shared_social,
                    workspace_description_draft,
                    workspace_thumbnail_notes,
                    workspace_shorts_ideas_draft,
                    workspace_message
                ]
            )

            workspace_save_button.click(
                save_project_workspace,
                inputs=[
                    workspace_project_picker,
                    workspace_title,
                    workspace_content_type,
                    workspace_game_topic,
                    workspace_status,
                    workspace_publish_date,
                    workspace_project_notes,
                    workspace_script_written,
                    workspace_gameplay_recorded,
                    workspace_voiceover_recorded,
                    workspace_editing_complete,
                    workspace_thumbnail_finished,
                    workspace_description_done,
                    workspace_uploaded_scheduled,
                    workspace_shared_social,
                    workspace_description_draft,
                    workspace_thumbnail_notes,
                    workspace_shorts_ideas_draft
                ],
                outputs=[workspace_overview, workspace_project_picker, workspace_message]
            )

            workspace_titles_button.click(
                project_generate_titles,
                inputs=[workspace_project_picker, workspace_project_notes, workspace_description_draft, workspace_thumbnail_notes, workspace_shorts_ideas_draft],
                outputs=workspace_ai_output,
                show_progress="full"
            )

            workspace_description_button.click(
                project_generate_description,
                inputs=[workspace_project_picker, workspace_project_notes, workspace_description_draft, workspace_thumbnail_notes, workspace_shorts_ideas_draft],
                outputs=workspace_ai_output,
                show_progress="full"
            )

            workspace_thumbnail_button.click(
                project_generate_thumbnail,
                inputs=[workspace_project_picker, workspace_project_notes, workspace_description_draft, workspace_thumbnail_notes, workspace_shorts_ideas_draft],
                outputs=workspace_ai_output,
                show_progress="full"
            )

            workspace_shorts_button.click(
                project_generate_shorts,
                inputs=[workspace_project_picker, workspace_project_notes, workspace_description_draft, workspace_thumbnail_notes, workspace_shorts_ideas_draft],
                outputs=workspace_ai_output,
                show_progress="full"
            )

            workspace_review_button.click(
                project_review,
                inputs=[workspace_project_picker, workspace_project_notes, workspace_description_draft, workspace_thumbnail_notes, workspace_shorts_ideas_draft],
                outputs=workspace_ai_output,
                show_progress="full"
            )



    with gr.Tab("🤖 AI Tools"):
        gr.Markdown("## 🤖 AI Tools\n\nAnalyze videos, improve thumbnails, generate titles, optimize SEO, write descriptions, and brainstorm content ideas.")


        with gr.Accordion("🤖 Coach Chat", open=True):
            gr.Markdown(
                """
                ## 🤖 Coach Chat
                Ask your AI Creator Coach what to work on next, what to improve, or how to grow your channel.

                Coach Chat uses your saved profile, calendar, projects, reviews, analytics, and Creator Health data.
                """
            )

            coach_question = gr.Textbox(
                label="Ask Coach Chat",
                placeholder="Example: What should I work on today?",
                lines=3
            )

            coach_button = gr.Button("Ask Coach")
            coach_output = gr.Markdown()

            coach_button.click(
                ask_creator_coach,
                inputs=coach_question,
                outputs=coach_output,
                show_progress="full"
            )

        with gr.Accordion("🎥 Video Analyzer", open=True):
            gr.Markdown(
                """
                ## 🎥 Video Analyzer
                Upload a long-form video, Short, Reel, TikTok, or Facebook Reel and get creator feedback. Channel Coach will sample frames and give pacing, hook, thumbnail, title, and editing advice.
                """
            )

            analyzer_upload = gr.Video(label="Upload Video")

            analyzer_type = gr.Dropdown(
                [
                    "Long-form YouTube Video",
                    "YouTube Short",
                    "TikTok",
                    "Instagram Reel",
                    "Facebook Reel"
                ],
                value="Long-form YouTube Video",
                label="Video Type"
            )

            analyzer_notes = gr.Textbox(
                label="Optional Notes",
                lines=6,
                placeholder="Example: This is my Ice Rod guide. Tell me what to cut, where to add text, and if the pacing feels good."
            )

            analyzer_button = gr.Button("🎥 Analyze Video")
            analyzer_output = gr.Textbox(label="Video Feedback", lines=18)


        with gr.Accordion("📚 Review History", open=False):
            review_history_output = gr.HTML(value=render_video_review_history())
            review_history_refresh = gr.Button("🔄 Refresh Review History")

            review_history_refresh.click(
                render_video_review_history,
                inputs=[],
                outputs=review_history_output
            )

        analyzer_button.click(
            video_analyzer_with_history,
            inputs=[analyzer_upload, analyzer_notes, analyzer_type],
            outputs=[analyzer_output, review_history_output],
            show_progress="full"
        )


        with gr.Accordion("🧠 Creator Memory Insights", open=False):
            gr.Markdown(
                """
                Generate pattern-based insights from your saved video reviews. Channel Coach will look for repeated strengths, weak spots, score trends, and your next best focus.
                """
            )
            creator_memory_snapshot = gr.HTML(value=render_creator_memory_snapshot())
            creator_memory_button = gr.Button("✨ Generate Creator Insights")
            creator_memory_output = gr.Textbox(label="Creator Memory Insights", lines=16)

            creator_memory_button.click(
                generate_creator_memory_insights,
                inputs=[],
                outputs=creator_memory_output,
                show_progress="full"
            )


        with gr.Accordion("🖼 Thumbnail Review", open=False):
            thumbnail_input = gr.Image(type="filepath", label="Upload Thumbnail")
            thumbnail_button = gr.Button("🖼 Review Thumbnail")
            thumbnail_output = gr.Textbox(label="Thumbnail Feedback", lines=16)

            thumbnail_button.click(
                analyze_thumbnail,
                inputs=thumbnail_input,
                outputs=thumbnail_output,
                show_progress="full"
            )



        with gr.Accordion("🏷 Title Generator", open=False):
            title_input = gr.Textbox(label="Video Idea", lines=4)
            title_platform = gr.Dropdown(
                ["YouTube Shorts", "TikTok", "Instagram Reels", "YouTube Long Form"],
                value="YouTube Shorts",
                label="Platform"
            )
            title_tone = gr.Dropdown(
                ["Bold", "Funny", "Friendly", "Casual", "Professional"],
                value="Bold",
                label="Tone"
            )
            title_button = gr.Button("✨ Generate Titles")
            title_output = gr.Textbox(label="Title Ideas", lines=12)

            title_button.click(
                generate_titles,
                inputs=[title_input, title_platform, title_tone],
                outputs=title_output,
                show_progress="full"
            )


        with gr.Accordion("🔍 SEO Optimizer", open=False):
            seo_input = gr.Textbox(label="Video Idea", lines=4)
            seo_platform = gr.Dropdown(
                ["YouTube Shorts", "TikTok", "Instagram Reels", "YouTube Long Form"],
                value="YouTube Shorts",
                label="Platform"
            )
            seo_niche = gr.Textbox(label="Niche", value="Gaming creator")
            seo_button = gr.Button("🔍 Generate SEO Plan")
            seo_output = gr.Textbox(label="SEO Results", lines=14)

            seo_button.click(
                seo_help,
                inputs=[seo_input, seo_platform, seo_niche],
                outputs=seo_output,
                show_progress="full"
            )


        with gr.Accordion("📝 Description Writer", open=False):
            desc_input = gr.Textbox(label="Video Idea", lines=4)
            desc_platform = gr.Dropdown(
                ["YouTube Shorts", "TikTok", "Instagram Reels", "YouTube Long Form"],
                value="YouTube Shorts",
                label="Platform"
            )
            desc_niche = gr.Textbox(label="Niche", value="Gaming creator")
            desc_button = gr.Button("📝 Write Description")
            desc_output = gr.Textbox(label="Description", lines=14)

            desc_button.click(
                description_help,
                inputs=[desc_input, desc_platform, desc_niche],
                outputs=desc_output,
                show_progress="full"
            )


        with gr.Accordion("💡 Content Ideas", open=False):
            niche_input = gr.Textbox(label="Niche", value="Retro gaming")
            topic_input = gr.Textbox(label="Game or Topi
