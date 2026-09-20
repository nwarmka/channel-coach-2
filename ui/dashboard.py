Supabase package available: True
SUPABASE_URL configured: True
Supabase key configured: True
Supabase ready: True
Traceback (most recent call last):
  File "/opt/render/project/src/app.py", line 6, in <module>
    from ui.dashboard import build_dashboard_page
  File "/opt/render/project/src/ui/dashboard.py", line 21
    css = """
          ^
SyntaxError: unterminated triple-quoted string literal (detected at line 326)
==> Exited with status 1
==> Common ways to troubleshoot your deploy: https://render.com/docs/troubleshooting-deploys
==> Port scan timeout reached, no open ports detected. Bind your service to at least one port. If you don't need to receive traffic on any port, create a background worker instead.
==> Docs on specifying a port: https://render.com/docs/web-services#port-binding
