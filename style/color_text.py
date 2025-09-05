class color_text:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

   CMS_yellow = '#F5BB54'
   CMS_green = '#607641' 

def print_error(message):
   print(f"{color_text.RED}[ERROR]{color_text.END} {message}")
def print_warning(message):
   print(f"{color_text.YELLOW}[WARNING]{color_text.END} {message}")
def print_info(message):
   print(f"{color_text.BLUE}[INFO]{color_text.END} {message}")
def print_success(message):
   print(f"{color_text.GREEN}[DONE!]{color_text.END} {message}")
def print_bold(message):
   print(f"{color_text.BOLD}{message}{color_text.END}")
def print_boldHeader(header, message):
   print(f"{color_text.BOLD}{header}{color_text.END} {message}")
def print_addition(message):
   print_boldHeader("[+]", message)
def print_executing(message):
   print(f"{color_text.GREEN}[EXE]{color_text.END} {message}")