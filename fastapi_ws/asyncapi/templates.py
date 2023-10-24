def asyncapi_html(title: str, asyncapi_path: str):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>{title}</title>
      <link rel="stylesheet" href="https://unpkg.com/@asyncapi/react-component@latest/styles/default.min.css">
    </head>
    <body>
      <div id="asyncapi"></div>
      
      <script src="https://unpkg.com/@asyncapi/react-component@latest/browser/standalone/index.js"></script>
      <script>
        AsyncApiStandalone.render({{
          schema: {{
            url: '{asyncapi_path}',
          }},
          config: {{
            show: {{
              sidebar: true,
            }}
          }},
       }}, document.getElementById('asyncapi'));
      </script>
    </body>
    </html>
    """
