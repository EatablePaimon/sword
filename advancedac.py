import os
import concurrent.futures
import threading
from collections import defaultdict, deque
from threading import Lock

class ACNode:
    __slots__ = ('children', 'fail', 'output', 'word_length')
    def __init__(self):
        self.children = {}          
        self.fail = None            
        self.output = []            
        self.word_length = 0        

class AdvancedAC:
    def __init__(self):
        self.root = ACNode()
        self.max_length = 0         
        self.word_source = {}      
        self.lock = Lock()          
        self._built = False         

    def add_word(self, word, source=None):
        
        if not word:
            return
        
        self.max_length = max(self.max_length, len(word))
        node = self.root
        
        for char in word:
            if char not in node.children:
                node.children[char] = ACNode()
            node = node.children[char]
        
        node.output.append({
            "word": word,
            "source": source,
            "length": len(word)
        })
        
        if word not in self.word_source and source:
            self.word_source[word] = source
    
    def build_fail_pointers(self):
        queue = deque()
        
        for char, child in self.root.children.items():
            child.fail = self.root  
            queue.append(child)
        
        # BFS构建失败指针
        while queue:
            current_node = queue.popleft()
            
            for char, child_node in current_node.children.items():
                queue.append(child_node)
                fail_node = current_node.fail
                while fail_node and char not in fail_node.children:
                    fail_node = fail_node.fail
                if fail_node and char in fail_node.children:
                    child_node.fail = fail_node.children[char]
                else:
                    child_node.fail = self.root
                child_node.output += child_node.fail.output
    
    def build_from_txt(self, dir_path):
        category_words = defaultdict(list)
        
        for root_dir, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root_dir, file)
                    try:
                        category = os.path.splitext(file)[0]
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                word = line.strip()
                                if word:
                                    category_words[category].append(word)
                                    self.add_word(word, source=category)
                    except Exception as e:
                        print(f"加载文件失败 {file_path}: {str(e)}")
        
        self.build_fail_pointers()
        self._built = True
        return self

    def scan_text(self, text):
        results = []
        current = self.root
        
        for index, char in enumerate(text):
            while current != self.root and char not in current.children:
                current = current.fail
            
            if char in current.children:
                current = current.children[char]
            else:
                current = self.root

            if current.output:
                for word_info in current.output:
                    start_pos = index - word_info["length"] + 1
                    results.append((
                        word_info["word"],
                        start_pos,
                        index,
                        word_info["source"]
                    ))
        
        return results

    def _contains_sensitive(self, text):
        current = self.root
        
        for char in text:
            while current != self.root and char not in current.children:
                current = current.fail
            
            if char in current.children:
                current = current.children[char]
            else:
                current = self.root
            
            if current.output:
                return True
        
        return False

    def contains_sensitive(self, text, chunk_size=5000):
        if not self.root or not text:
            return False
        
        n = len(text)
        if n <= chunk_size + self.max_length - 1:
            return self._contains_sensitive(text)
        
        overlap = self.max_length 
        chunks = []
        start = 0
        
        while start < n:
            end = min(n, start + chunk_size + overlap)
            chunks.append(text[start:end])
            start += chunk_size
        
        if len(chunks) == 1:
            return self._contains_sensitive(chunks[0])
        
        found = False
        event = threading.Event()
        
        def check_chunk(chunk):
            nonlocal found
            if event.is_set():
                return False
            if self._contains_sensitive(chunk):
                with self.lock:  
                    found = True
                event.set()
                return True
            return False
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(check_chunk, chunk) for chunk in chunks]
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    return True
        
        return found