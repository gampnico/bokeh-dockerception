from datetime import datetime

import holoviews as hv
import numpy as np
import pandas as pd
import panel as pn
import param
from bokeh.models import DatetimeTickFormatter, PrintfTickFormatter
from dateutil.tz import UTC

pn.extension(design="material", sizing_mode="stretch_width")
pn.extension(loading_spinner="dots", loading_color="#00aa41", template="material")
pn.param.ParamMethod.loading_indicator = True
hv.extension("bokeh")
hv.renderer("bokeh").webgl = True


class Artist:
    def __init__(self):
        super().__init__()
        self.defaults = self.get_default_opts()
        self.set_defaults(
            {
                "ylabel": "Runoff (Mt)",
                "yformatter": PrintfTickFormatter(format="%.2f"),
                "padding": (0.1, (0, 0.1)),
                "ylim": (0, None),
                "autorange": "y",
            }
        )
        self.palette = self.get_color_palette("lines_jet_r")

    def get_default_opts(self) -> dict:
        """Default options for Bokeh figures.

        Returns
        -------
        dict
            Default options for Bokeh figures. Not necessarily
            compatible with Holoviews or Geoviews objects.
        """
        default_options = {
            "aspect": 2,
            "active_tools": ["pan", "wheel_zoom"],
            "fontscale": 1.2,
            "bgcolor": "white",
            "backend_opts": {"title.align": "center", "toolbar.autohide": True},
            "show_frame": False,
            "margin": 0,
            "border": 0,
        }

        return default_options

    def get_all_palettes(self) -> dict:
        """Get all valid preset colour palettes.

        Returns
        -------
        dict
            Preset colour palettes.
        """
        palettes = {
            "brown_blue_pastel": ("#e0beb3", "#b3d5e0", "#beacf6"),
            "brown_blue_vivid": ("#f6beac", "#ace4fc", "#beacf6"),
            "hillshade_glacier": ("#f6beac", "#ffffff", "#33b5cb"),
            "lines_jet_r": ("#ffffff", "#d62728", "#1f77b4"),
        }
        return palettes

    def get_color_palette(self, name: str) -> tuple:
        """Get a preset palette.

        Parameters
        ----------
        name : str
            Name of palette.

        Returns
        -------
        tuple[str]
            Palette of hex colours.
        """
        palettes = self.get_all_palettes()
        if name.lower() not in palettes.keys():
            try:
                palettes[name] = list(hv.Cycle.default_cycles[name])
            except:
                palette_names = "', '".join(palettes.keys())
                raise KeyError(f"{name} not found. Try: {palette_names}")

        return palettes[name]

    def set_defaults(self, updated_options: dict):
        """Set and overwrite default options for Bokeh figures.

        Parameters
        ----------
        updated_options : dict
            New key/value pairs which will overwrite the default options.
        """
        self.defaults.update(updated_options)

    def get_sine_data(self, size, scaling=1):
        x = np.linspace(0, 2 * np.pi, num=size)
        n = np.random.normal(scale=10 * scaling, size=x.size)
        y = np.abs(100 * np.sin(x) + n / 50)  # +2*(year - 2000)
        return x, y

    def get_synthetic_data(self, year, scale_offset=0):
        x_dates = pd.date_range(f"{year}-01-01", f"{year+1}-12-31", freq="1D", tz=UTC)
        x, y = self.get_sine_data(size=x_dates.size, scaling=year - scale_offset)
        df = pd.DataFrame(index=x_dates, data=y, columns=["data"])

        date_mask = self.get_date_mask(df, f"{year}-01-01", f"{year+1}-01-01")
        df[date_mask] = df[date_mask] + year / 1000
        plot_data = (
            df[date_mask]
            .groupby([df[date_mask].index.day_of_year])
            .mean()
            .rename_axis(index=["doy"])
        )

        plot_data.index = pd.to_datetime(plot_data.index, format="%j")
        return plot_data

    def plot_synthetic_data(
        self, title, label, ref_year=2017, cumulative=False
    ) -> hv.Overlay:
        geodetic_period = [2015, 2020]
        figures = []
        for year in np.arange(*geodetic_period):
            if not cumulative:
                plot_data = self.get_synthetic_data(year=year, scale_offset=2000)
            else:
                plot_data = self.get_synthetic_data(year=year)
                plot_data = plot_data.cumsum() / 1000
            figures = self.add_curve_to_figures(
                data=plot_data,
                key="data",
                figures=figures,
                line_color="grey",
                muted=True,
                line_width=0.8,
                # line_dash="dotted",
                label=f"{geodetic_period[0]}-{geodetic_period[-1]}",
            )

        plot_data = self.get_synthetic_data(year=ref_year)
        if not cumulative:
            plot_data = self.get_synthetic_data(year=year, scale_offset=2000)
        else:
            plot_data = self.get_synthetic_data(year=year)
            plot_data = plot_data.cumsum() / 1000
        figures = self.add_curve_to_figures(
            data=plot_data,
            key="data",
            figures=figures,
            line_color="#d62728",
            line_width=2.0,
            label=f"{ref_year}",
        )
        default_opts = self.get_default_opts()
        overlay = (
            hv.Overlay(figures)
            .opts(**default_opts)
            .opts(
                aspect=2,
                ylabel=f"{label}",
                title=f"{title}",
                xlabel="Month",
                # xformatter=f"%j",
                xformatter=DatetimeTickFormatter(months="%B"),
                tools=["xwheel_zoom", "xpan"],
                active_tools=["xwheel_zoom"],
                legend_position="top",
                legend_opts={
                    "orientation": "vertical",
                    # "css_variables": {"font-size": "1em", "display": "inline"},
                },
            )
        )

        return overlay

    def get_date_mask(self, dataframe: pd.DataFrame, start_date: str, end_date: str):
        date_mask = (
            datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=UTC)
            <= dataframe.index
        ) & (
            dataframe.index
            <= datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=UTC)
        )
        return date_mask

    def add_curve_to_figures(
        self,
        figures: list,
        data: dict,
        key: str,
        label: str = "",
        line_width=0.8,
        **kwargs,
    ) -> list:
        if not label:
            label = self.get_label_from_key(key)
        curve = hv.Curve(data[key], label=label).opts(line_width=line_width, **kwargs)
        figures.append(curve)
        return figures

    def set_layout(self, figures: list) -> hv.Layout:
        """Compose Layout from a sequence of overlays or layouts.

        Dynamically adds a sequence of overlays to a layout.

        Parameters
        ----------
        figures : list[hv.Overlay|hv.Layout]
            A sequence of figures.
        """
        # columns = len(figures)
        if isinstance(figures, list):
            layout = figures[0]
            if len(figures) > 1:
                layout = figures
            layout = hv.Layout(layout).cols(2)
        else:
            layout = hv.Layout([figures])

        layout = layout.opts(sizing_mode="stretch_both")

        return layout

    def set_dashboard(self, figures: list):
        """Set dashboard from a sequence of figures.

        Parameters
        ----------
        figures : list[hv.Overlay|hv.Layout]
            A sequence of figures.
        """
        self.dashboard = self.set_layout(figures=figures).opts(
            shared_axes=False,
            title="Dashboard",
            fontsize={"title": 18},
            sizing_mode="scale_both",
            merge_tools=False,
        )
        return self.dashboard


class SineWave(param.Parameterized):
    N = param.Integer(default=200, bounds=(0, None))
    year = param.Selector(objects=range(2000, 2020), default=2017)
    cumulative = param.Boolean(False)

    def __init__(self, **params):
        super(SineWave, self).__init__(**params)
        self.figure = hv.Layout()
        self.binder = Artist()
        self.data = None
        self.plot = pn.pane.HoloViews(self.figure, sizing_mode="scale_both")
        self.set_plot()

    @param.depends(
        "N",
        "year",
        "cumulative",
        watch=True,
    )
    def set_plot(self):
        self.plot_dashboard(year=self.year)

    def plot_dashboard(self, year):
        figure = self.binder.plot_synthetic_data(
            title="Runoff",
            label="Runoff (Mt)",
            ref_year=self.year,
            cumulative=self.cumulative,
        )
        self.figure = self.binder.set_dashboard(figures=figure)
        self.plot.object = self.figure
