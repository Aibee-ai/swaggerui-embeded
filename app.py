import json

import requests
import streamlit as st
from streamlit_embeded import st_embeded

st.set_page_config(layout="wide", initial_sidebar_state='collapsed')


def main():
    st.info("由于 SwaggerUI 并不支持根据提供的 Auth Token 对应权限自动更新 API Spec，故有此工具解决这类问题")
    src = st.text_input("Spec Address", value="https://petstore.swagger.io/v2/swagger.json")
    if not src:
        st.warning('Spec Address is required')
        return 

    try:
        response = requests.get(src)
    except Exception as e:
        st.error(f'Fail to parse Spec from {src}')
        st.exception(e)
        return

    spec = response.json()
    auth_key = None
    token = None
    if spec.get('swagger') == '2.0':
        for itemx in spec.get('security', []):
            cfka = list(itemx.keys())[0]
            for cfkb, item in spec.get('securityDefinitions', {}).items():
                if cfka != cfkb:
                    continue
                if item.get('name') != 'Authorization':
                    continue
                auth_key = cfka
                token = st.text_input(item['name'] + '(Without Bearer Prefix)', type="password")
                if not token:
                    st.warning('Authorization Token required')
                    return

    if token:
        response = requests.get(src,  headers={'Authorization': f'Bearer {token}'})
    else:
        response = requests.get(src)

    spec = response.json()

    source = """
        <style>
        body {
            margin-bottom: 50px;
        }
        </style>
        <link rel="stylesheet" type="text/css" href="//cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.5.0/swagger-ui.min.css">
        <div id="swagger-ui"></div>
        <script src="//cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.5.0/swagger-ui-bundle.min.js"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.5.0/swagger-ui-standalone-preset.min.js"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/iframe-resizer/4.3.2/iframeResizer.contentWindow.min.js"></script>
        <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                onComplete: function(){
                    if (%s){
                        ui.preauthorizeApiKey('%s', 'Bearer %s');
                    }
                },
                spec: %s,
                dom_id: "#swagger-ui",
                deepLinking: true,
                filter: true,
                defaultModelsExpandDepth: -1,
                defaultModelExpandDepth: -1,
                displayRequestDuration: true,
                displayOperationId: false,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl,
                ],
                layout: "BaseLayout",
                withCredentials: false,
                persistAuthorization: true,
                tryItOutEnabled: true,
                queryConfigEnabled: true,
                requestSnippetsEnabled: true,
            })
            window.ui = ui;
        };
        </script>
    """ % ('true' if token else 'false', auth_key, token, json.dumps(spec))
    st_embeded(source, key='swaggerui')

    if st.sidebar.checkbox('Show OpenAPI in RAW'):
        st.json(spec)

if __name__ == '__main__':
    main()