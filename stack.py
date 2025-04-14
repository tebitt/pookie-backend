class Stack:
    def __init__(self):
        self._item = None
        self._has_new_item = False
    
    def put(self, item):
        """Replace the current item with a new one"""
        self._item = item
        self._has_new_item = True
    
    def get_latest(self, timeout=None):
        """Get the latest item if available"""
        if not self._has_new_item:
            raise TimeoutError("No new item available")
        
        self._has_new_item = False
        return self._item
    
    def has_new_item(self):
        """Check if a new unprocessed item is available"""
        return self._has_new_item
    
