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

User interface displaying L2 dashboard for specific glaciers.
"""

import panel as pn

from ...components.synthetic import SineWave


def get_sinewave_dashboard():
    """Get UI components for the dashboard.

    Returns
    -------
    pn.template.MaterialTemplate
        Dashboard interface.
    """
    rs = SineWave()

    """Widgets
    
    Note that some buttons are already declared in RegionSelection.
    """

    sidebar = [
        pn.Param(
            rs.param,
            name="",
        ),
    ]

    dashboard_content = [rs.plot]  # this is the dashboard content
    panel = pn.template.MaterialTemplate(
        title="Dockerception Dashboard",
        # busy_indicator=indicator_loading,
        sidebar=sidebar,
        logo="./static/img/dtc_logo_inv_min.png",
        main=dashboard_content,
        sidebar_width=250,
    )
    return panel
