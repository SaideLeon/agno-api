agno-api-89509583:~/agno-api{main}$ /nix/store/vwn2q58w5sx7iwwc79l50kl9pvb0jm7f-run-server
INFO:     Will watch for changes in these directories: ['/home/user/agno-api']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [232] using WatchFiles
INFO:     Started server process [284]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:42914 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:36224 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:36224 - "GET /favicon.ico HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:51718 - "GET /playground HTTP/1.1" 200 OK
INFO:app.routes.agent:Recebida requisição para /hierarchy: user_id=user-playground, instance_id=instance-playground
INFO:app.routes.agent:Payload recebido: {'user_id': 'user-playground', 'instance_id': 'instance-playground', 'router_instructions': 'Você é um roteador inteligente. Delegue a tarefa para o especialista adequado.', 'agents': [{'name': 'Analista Financeiro', 'role': 'Especialista em análise de ações e dados financeiros.', 'model_provider': 'GEMINI', 'model_id': 'gemini-1.5-flash', 'tools': [{'type': 'YFINANCE', 'config': {'stock_price': True, 'company_news': True}}]}, {'name': 'Pesquisador Web', 'role': 'Especialista em buscar informações na web.', 'model_provider': 'GEMINI', 'model_id': 'gemini-1.5-flash', 'tools': [{'type': 'DUCKDUCKGO'}]}]}
INFO:app.routes.agent:Hierarquia atualizada com sucesso.
INFO:     127.0.0.1:53988 - "PUT /agent/hierarchy HTTP/1.1" 200 OK
