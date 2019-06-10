""" Extensions to wtforms """

from wtforms import SelectMultipleField, widgets

class MultiCheckboxField(SelectMultipleField):
    """ Enables use of multiple checkboxes for forms """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
