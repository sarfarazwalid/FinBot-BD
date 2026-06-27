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

# 2. useConversations.ts - modify createConversation and imports
p = os.path.join(base, 'hooks', 'useConversations.ts')
with open(p, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'import { storage, generateConversationTitle } from "@/lib/storage";',
    'import { storage, generateConversationTitle, STORAGE_KEY, ACTIVE_KEY } from "@/lib/storage";'
)

old_create = '''  const createConversation = useCallback((): Conversation => {
    const newConv: Conversation = {
      id: crypto.randomUUID(),
      title: "New Conversation",
      createdAt: Date.now(),
      updatedAt: Date.now(),
      messages: [],
      language: "en",
      bank: undefined,
    };

    setConversations((prev) => [newConv, ...prev]);
    setActiveId(newConv.id);
    storage.saveConversations([newConv, ...conversations]);
    storage.saveActiveId(newConv.id);
    return newConv;
  }, [conversations]);'''

new_create = '''  const createConversation = useCallback((): Conversation => {
    const newConv: Conversation = {
      id: crypto.randomUUID(),
      title: "New Conversation",
      createdAt: Date.now(),
      updatedAt: Date.now(),
      messages: [],
      language: "en",
      bank: undefined,
    };

    // Read fresh from storage to avoid stale closure issues
    let latestConversations: Conversation[] = [];
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      latestConversations = stored ? JSON.parse(stored) : [];
    } catch {
      latestConversations = [];
    }

    // Atomically remove empty active conversation (if any)
    const filtered = latestConversations.filter(
      (c) => c.id !== activeId || c.messages.length > 0
    );
    const next = [newConv, ...filtered];

    setConversations(next);
    setActiveId(newConv.id);

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      // Storage full
    }
    localStorage.setItem(ACTIVE_KEY, newConv.id);

    if (activeId) {
      storage.clearDraft(activeId);
    }

    return newConv;
  }, [activeId]);'''

c = c.replace(old_create, new_create)
with open(p, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated useConversations.ts')

# 3. useChat.ts - add deleteConversation, activeConversation, update clearChat/goHome
p = os.path.join(base, 'hooks', 'useChat.ts')
with open(p, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'clearActiveConversation,\n    addMessage,',
    'clearActiveConversation,\n    deleteConversation,\n    addMessage,'
)

c = c.replace(
    '    clearActiveConversation,\n  });',
    '    deleteConversation,\n  });'
)

c = c.replace('const clearChat = useCallback(() => {\n    // Return to home — do NOT create new conversation\n    clearActiveConversation();\n  }, [clearActiveConversation]);', 'const clearChat = useCallback(() => {\n    if (activeConversation && activeConversation.messages.length === 0) {\n      deleteConversation(activeConversation.id);\n    }\n    clearActiveConversation();\n  }, [clearActiveConversation, deleteConversation, activeConversation]);')

c = c.replace('const goHome = useCallback(() => {\n    clearActiveConversation();\n  }, [clearActiveConversation]);', 'const goHome = useCallback(() => {\n    if (activeConversation && activeConversation.messages.length === 0) {\n      deleteConversation(activeConversation.id);\n    }\n    clearActiveConversation();\n  }, [clearActiveConversation, deleteConversation, activeConversation]);')

c = c.replace(
    '  return {\n    messages,\n    loading,\n    error,\n    send,\n    clearChat,\n    goHome,\n    activeId,\n    setActiveConversation,\n  };',
    '  return {\n    messages,\n    loading,\n    error,\n    send,\n    clearChat,\n    goHome,\n    activeId,\n    activeConversation,\n    setActiveConversation,\n  };'
)

with open(p, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated useChat.ts')
