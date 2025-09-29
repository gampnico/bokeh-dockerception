"""
Copyright 2025 DTCG Contributors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

===

Testing ground for Boke apps via Docker-in-Docker.
"""

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from panel.io.fastapi import add_application

from dockerception.ui.interface.apps.pn_sinewave import get_sinewave_dashboard

logger = logging.getLogger(__name__)

logger.info("Initialising app")
app = FastAPI(root_path="/dockerception")

BASE_DIR = Path(__file__).resolve().parent
logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info("Mounting static files...")
# app.mount("/static", StaticFiles(directory=f"{BASE_DIR/'static'}"), name="static")
templates = Jinja2Templates(directory=f"{BASE_DIR/'templates'}")
hostname = os.getenv("WS_ORIGIN", "127.0.0.1")
logger.info(f"Hostname: {hostname}")
port = 8080

"""Middleware

TODO: sanitise user shapefiles
TODO: HTTPSRedirectMiddleware
"""
app.add_middleware(  # TODO: Bremen cluster support
    TrustedHostMiddleware,
    allowed_hosts=[
        hostname,
        "localhost",
        "dtcg.github.io",
        "bokeh.oggm.org",
        "bokeh.oggm.org/dockerception",
    ],
)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    file_name = "favicon.ico"
    file_path = Path(app.root_path)
    file_path = file_path / "static" / file_name

    return FileResponse(
        path=file_path,
        headers={"Content-Disposition": "attachment; filename=" + file_name},
    )


"""Error handling"""


@app.exception_handler(404)
async def get_404_handler(request, __):
    """Get and handle 404 errors."""
    return templates.TemplateResponse("404.html", {"request": request})


"""Serve dashboard"""


@app.get("/")
async def read_root(request: Request):
    """Get homepage.

    This just redirects to the dashboard, but can be extended if
    multiple apps are implemented.
    """
    logger.info("Redirect from root to /dockerception/app")
    return RedirectResponse(url=f"{app.root_path}/app")


@add_application(
    "/app",
    app=app,
    title="Dockerception Dashboard",
    # address=hostname,
    # port=f"{port}",
    # # show=False,
    # allow_websocket_origin=[
    #     f"{hostname}:{port}",
    #     f"localhost:{port}",
    #     f"0.0.0.0:{port}",
    # ],
)
def get_dashboard():
    """Get the main dashboard"""
    logger.info("Loading dashboard")
    return get_sinewave_dashboard()
