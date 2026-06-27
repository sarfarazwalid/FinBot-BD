import os

base = r'c:\Important\FinBot BD\frontend\src'

# 1. storage.ts - export constants
p = os.path.join(base, 'lib', 'storage.ts')
with open(p, 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('const STORAGE_KEY = "finbot_bd_conversations";', 'export const STORAGE_KEY = "finbot_bd_conversations";')
c = c.replace('const ACTIVE_KEY = "finbot_bd_active_id";', 'export const ACTIVE_KEY = "finbot_bd_active_id";')
c = c.replace('const SIDEBAR_SCROLL_KEY = "finbot_bd_sidebar_scroll";', 'export const SIDEBAR_SCROLL_KEY = "finbot_bd_sidebar_scroll";')
c = c.replace('const DRAFTS_KEY = "finbot_bd_drafts";', 'export const DRAFTS_KEY = "finbot_bd_drafts";')
with open(p, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated storage.ts')
