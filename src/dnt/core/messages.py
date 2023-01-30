from typing import Dict, List, Optional
import numpy as np
from dnt.core.utils import (
    NOTSET,
    lvl_to_num
)


class Message:
    def __init__(self, msg: Dict):
        self.level = msg.get("level", NOTSET)
        self.lvl_no = lvl_to_num(self.level)
        self.message = msg

class MsgRcv:
    """
    A message receiver class to dispatch messages to each destination of a specific message group.
    """
    def __init__(self, config: Dict, formatter_dic: Dict, filterer_dic: Dict) -> None:
        self.config = config
        self.dest = self.config.get("dest")
        self.level = self.config.get("level", "NOTSET")
        self.formatter_dic = formatter_dic
        self.filterer_dic = filterer_dic

        self.filterer = self.config.get("filterer") # 1 filterer or a list of filterers
        self.formatter = self.config.get("formatter") # 1 formatter
        self.formatter, self.filterer = self._load_styler()

    def _load_styler(self):
        formatter = None
        filterer = None
        formatter_name = self.config.get("formatter") # 1 formatter
        filterer_name = self.config.get("filterer") # 1 filterer or a list of filterers

        if formatter_name is not None:
            formatter = self.formatter_dic.get(formatter_name)

        if filterer_name is not None:
            filterer = [self.filterer_dic.get(fn) for fn in filterer_name]

        return formatter, filterer

    def _filter_msg(self, msg_ls: List[Message]) -> List:
        """
        Filter messages according to specific rules.
        """
        if self.filterer is not None:
            filterer_ls = self.filterer if isinstance(self.filterer, list) else [self.filterer]
            
            keep_flag_ls = []
            for msg in msg_ls:
                keep_flag_ls.append(
                    np.prod([f.filter(msg) for f in filterer_ls])
                )
            msg_ls = [msg for n, msg in enumerate(msg_ls) if keep_flag_ls[n] > 0]

        level = lvl_to_num(self.level)
        res_ls = [msg for msg in msg_ls if msg.lvl_no >= level]
        return res_ls
    
    def _format_msg(self, msg_ls: List[Message]) -> List:
        """
        Render the messages in a specific format, if no formatter assigned, will pass it to Destination for formatting.
        """
        if self.formatter is not None:
            res_ls = [self.formatter.format(msg) for msg in msg_ls]
            return res_ls
        else:
            return msg_ls
    
    def deliver_msg(self, msg_ls: List[Message], subject: Optional[str]=None):      
        """
        Deliver messages to a Destination in a dict manner.
        """
        msg_ls = self._filter_msg(msg_ls)
        res_ls = self._format_msg(msg_ls)
        return (
            self.dest, 
            {
                "subject": subject, 
                "messages": res_ls
            }
        )

class MsgGrp:
    """
    A message group class to dispatch messages to the destinations assigned in the group.
    """
    def __init__(self, name, config: List, formatter_dic: Dict, filterer_dic: Dict) -> None:
        self.name = name
        self.config = config
        self.formatter_dic = formatter_dic
        self.filterer_dic = filterer_dic
        
    def deliver_msg(self, msg_ls: List[Message], subject: Optional[str]=None):
        """
        Delivery messages to all the destinations in the group.
        """
        res_ls = []
        for cfg in self.config:
            rcv = MsgRcv(cfg, self.formatter_dic, self.filterer_dic)
            res_ls.append(rcv.deliver_msg(msg_ls, subject))
        return res_ls
