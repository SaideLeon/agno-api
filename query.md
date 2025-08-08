lication shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [21008]
INFO:     Started server process [21620]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:57888 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:38372 - "GET /playground HTTP/1.1" 200 OK
INFO:     127.0.0.1:57752 - "GET /playground HTTP/1.1" 200 OK
WARNING:  WatchFiles detected changes in 'app/main.py'. Reloading...
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [21620]
INFO:     Started server process [22727]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:40280 - "GET /playground HTTP/1.1" 200 OK
INFO:     127.0.0.1:46572 - "PUT /agent/hierarchy HTTP/1.1" 422 Unprocessable Entity
WARNING:  WatchFiles detected changes in 'app/routes/agent.py'. Reloading...
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [22727]
INFO:     Started server process [23310]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:32938 - "GET /playground HTTP/1.1" 200 OK
INFO:     127.0.0.1:32938 - "PUT /agent/hierarchy HTTP/1.1" 422 Unprocessable Entity
WARNING:  WatchFiles detected changes in 'app/routes/agent.py'. Reloading...
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [23310]
INFO:     Started server process [23812]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:38110 - "GET /playground HTTP/1.1" 200 OK
INFO:     127.0.0.1:38110 - "PUT /agent/hierarchy HTTP/1.1" 422 Unprocessable Entity
WARNING:  WatchFiles detected changes in 'app/models/instance.py'. Reloading...
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [23812]
INFO:     Started server process [24472]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
WARNING:  WatchFiles detected changes in 'app/models/instance.py'. Reloading...
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [24472]
Process SpawnProcess-16:
Traceback (most recent call last):
  File "/usr/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
    self.run()
  File "/usr/lib/python3.11/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
  File "/home/user/agno-api/.venv/lib/python3.11/site-packages/uvicorn/_subprocess.py", line 76, in subprocess_started
    target(sockets=sockets)
  File "/home/user/agno-api/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 61, in run
    return asyncio.run(self.serve(sockets=sockets))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
  File "/home/user/agno-api/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 68, in serve
    config.load()
  File "/home/user/agno-api/.venv/lib/python3.11/site-packages/uvicorn/config.py", line 467, in load
    self.loaded_app = import_from_string(self.app)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/user/agno-api/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 21, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/home/user/agno-api/app/main.py", line 13, in <module>
    from app.models.instance import AgentInstance
  File "/home/user/agno-api/app/models/instance.py", line 25, in <module>
    class ToolConfig(BaseModel):
  File "/home/user/agno-api/app/models/instance.py", line 30, in ToolConfig
    @validator('type')
     ^^^^^^^^^
NameError: name 'validator' is not defined
