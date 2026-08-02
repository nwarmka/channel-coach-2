    app.load(
        restore_saved_session,
        inputs=[saved_login],
        outputs=[login_status, workspace_name, saved_login],
    ).then(
        load_workspace_ui,
        inputs=[workspace_name],
        outputs=[
            workspace_indicator,
            dashboard_output,
            cc_calendar_output,
            cc_upcoming_output,
            cc_calendar_item_picker,
            calendar_item_picker,
            workspace_project_picker,
            analytics_output,
            onboarding_output,
            profile_channel_name,
            profile_creator_name,
            profile_niche,
            profile_target_audience,
            profile_content_style,
            profile_current_games,
            profile_main_platforms,
            profile_goals,
            profile_preferred_tone,
            profile_things_to_avoid
        ]
    )
 
      
    
 
      
    
 
      
