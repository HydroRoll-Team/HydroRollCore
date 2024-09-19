"""HydroRoll-Team/echo
水系跨平台事件标准(cross-platform event standard): Event Communication and Harmonization across Online platforms.
:ref: https://github/com/HydroRoll-Team/echo
:ref: https://echo.hydroroll.team
"""

class Event(object):
    """事件基类
    :ref: https://echo.hydroroll.team/Event/#0_event
    """
    def __init__(self, event_type, data, metadata):
        self.event_type = event_type
        self.data = data
        self.metadata = metadata

class WorkFlow(Event):
    """workflow
    :ref: https://echo.hydroroll.team/Event/#1_workflow
    """
    def __init__(self, data, metadata):
        super().__init__('workflow', data, metadata)

class CallBack(Event):
    """callback
    :ref: https://echo.hydroroll.team/Event/#4_callback
    """
    def __init__(self, data, metadata):
        super().__init__('callback', data, metadata)

class Message(Event):
    """message
    :ref: https://echo.hydroroll.team/Event/#2_message
    """
    def __init__(self, data, metadata):
        super().__init__('message', data, metadata)

class Reaction(Event):
    """reaction
    :ref: https://echo.hydroroll.team/Event/#3_reaction
    """
    def __init__(self, data, metadata):
        super().__init__('reaction', data, metadata)

class Typing(Event):
    """typing
    :ref: https://echo.hydroroll.team/Event/#5_typing
    """
    def __init__(self, data, metadata):
        super().__init__('typing', data, metadata)

class UserJoin(Event):
    """user join
    :ref: https://echo.hydroroll.team/Event/#6_user_join
    """
    def __init__(self, data, metadata):
        super().__init__('user_join', data, metadata)

class UserLeave(Event):
    """user leave
    :ref: https://echo.hydroroll.team/Event/#7_user_leave
    """
    def __init__(self, data, metadata):
        super().__init__('user_leave', data, metadata)

class FileShare(Event):
    """file share
    :ref: https://echo.hydroroll.team/Event/#8_file_share
    """
    def __init__(self, data, metadata):
        super().__init__('file_share', data, metadata)

class Mention(Event):
    """mention
    :ref: https://echo.hydroroll.team/Event/#9_mention
    """
    def __init__(self, data, metadata):
        super().__init__('mention', data, metadata)

class ChannelCreate(Event):
    """channel create
    :ref: https://echo.hydroroll.team/Event/#10_channel_create
    """
    def __init__(self, data, metadata):
        super().__init__('channel_create', data, metadata)

class ChannelDelete(Event):
    """channel delete
    :ref: https://echo.hydroroll.team/Event/#11_channel_delete
    """
    def __init__(self, data, metadata):
        super().__init__('channel_delete', data, metadata)

class ChannelUpdate(Event):
    """channel update
    :ref: https://echo.hydroroll.team/Event/#12_channel_update
    """
    def __init__(self, data, metadata):
        super().__init__('channel_update', data, metadata)

class UserUpdate(Event):
    """user update
    :ref: https://echo.hydroroll.team/Event/#13_user_update
    """
    def __init__(self, data, metadata):
        super().__init__('user_update', data, metadata)