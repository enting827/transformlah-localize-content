<template>
  <div class="generator-container">
    <!-- Left Sidebar -->
    <div :class="['sidebar', { 'collapsed': isSidebarCollapsed }]">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="startNewChat">
          <svg class="plus-icon" viewBox="0 0 24 24" fill="none">
            <path d="M12 4V20M4 12H20" stroke="currentColor" stroke-width="2"/>
          </svg>
          New Chat
        </button>
        <button class="collapse-btn" @click="toggleSidebar">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M15 6L9 12L15 18" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
      </div>

      <div class="search-container">
        <div class="search-input-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none">
            <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="currentColor" stroke-width="2"/>
          </svg>
          <input 
            type="text" 
            placeholder="Search chats..." 
            v-model="searchQuery"
            class="search-input"
          >
        </div>
      </div>

      <div class="chat-history">
        <!-- Hardcoded chat history items -->
        <div 
          v-for="chat in filteredChatHistory" 
          :key="chat.id"
          :class="['chat-history-item', { 'active': currentChatId === chat.id }]"
          @click="loadChat(chat.id)"
        >
          <svg class="chat-icon" viewBox="0 0 24 24" fill="none">
            <path d="M8 12H8.01M12 12H12.01M16 12H16.01M21 12C21 16.4183 16.9706 20 12 20C10.4607 20 9.01172 19.6565 7.74467 19.0511L3 20L4.39499 16.28C3.51156 15.0423 3 13.5743 3 12C3 7.58172 7.02944 4 12 4C16.9706 4 21 7.58172 21 12Z" stroke="currentColor" stroke-width="2"/>
          </svg>
          <span class="chat-title">{{ chat.title }}</span>
          <button class="delete-chat-btn" @click.stop="deleteChat(chat.id)">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M6 18L18 6M6 6L18 18" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Chat Interface -->
    <div class="chat-section">
      <!-- Header -->
      <div class="chat-header">
        <div class="header-left">
          <button v-if="isSidebarCollapsed" class="expand-sidebar-btn" @click="toggleSidebar">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M4 6H20M4 12H20M4 18H20" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </div>
        <div class="header-right">
          <button class="settings-btn" @click="toggleSettings">
            <svg viewBox="0 0 24 24" fill="none" class="settings-icon">
              <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" stroke-width="2"/>
              <path d="M19.4 15C19.2669 15.3016 19.2272 15.6362 19.286 15.9606C19.3448 16.285 19.4995 16.5843 19.73 16.82L19.79 16.88C19.976 17.0657 20.1235 17.2863 20.2241 17.5291C20.3248 17.7719 20.3766 18.0322 20.3766 18.295C20.3766 18.5578 20.3248 18.8181 20.2241 19.0609C20.1235 19.3037 19.976 19.5243 19.79 19.71C19.6043 19.896 19.3837 20.0435 19.1409 20.1441C18.8981 20.2448 18.6378 20.2966 18.375 20.2966C18.1122 20.2966 17.8519 20.2448 17.6091 20.1441C17.3663 20.0435 17.1457 19.896 16.96 19.71L16.9 19.65C16.6643 19.4195 16.365 19.2648 16.0406 19.206C15.7162 19.1472 15.3816 19.1869 15.08 19.32C14.7842 19.4468 14.532 19.6572 14.3543 19.9255C14.1766 20.1938 14.0813 20.5082 14.08 20.83V21C14.08 21.5304 13.8693 22.0391 13.4942 22.4142C13.1191 22.7893 12.6104 23 12.08 23C11.5496 23 11.0409 22.7893 10.6658 22.4142C10.2907 22.0391 10.08 21.5304 10.08 21V20.91C10.0723 20.579 9.96512 20.258 9.77251 19.9887C9.5799 19.7194 9.31074 19.5143 9 19.4C8.69838 19.2669 8.36381 19.2272 8.03941 19.286C7.71502 19.3448 7.41568 19.4995 7.18 19.73L7.12 19.79C6.93425 19.976 6.71368 20.1235 6.47088 20.2241C6.22808 20.3248 5.96783 20.3766 5.705 20.3766C5.44217 20.3766 5.18192 20.3248 4.93912 20.2241C4.69632 20.1235 4.47575 19.976 4.29 19.79C4.10405 19.6043 3.95653 19.3837 3.85588 19.1409C3.75523 18.8981 3.70343 18.6378 3.70343 18.375C3.70343 18.1122 3.75523 17.8519 3.85588 17.6091C3.95653 17.3663 4.10405 17.1457 4.29 16.96L4.35 16.9C4.58054 16.6643 4.73519 16.365 4.794 16.0406C4.85282 15.7162 4.81312 15.3816 4.68 15.08C4.55324 14.7842 4.34276 14.532 4.07447 14.3543C3.80618 14.1766 3.49179 14.0813 3.17 14.08H3C2.46957 14.08 1.96086 13.8693 1.58579 13.4942C1.21071 13.1191 1 12.6104 1 12.08C1 11.5496 1.21071 11.0409 1.58579 10.6658C1.96086 10.2907 2.46957 10.08 3 10.08H3.09C3.42099 10.0723 3.742 9.96512 4.0113 9.77251C4.28059 9.5799 4.48572 9.31074 4.6 9C4.73312 8.69838 4.77282 8.36381 4.714 8.03941C4.65519 7.71502 4.50054 7.41568 4.27 7.18L4.21 7.12C4.02405 6.93425 3.87653 6.71368 3.77588 6.47088C3.67523 6.22808 3.62343 5.96783 3.62343 5.705C3.62343 5.44217 3.67523 5.18192 3.77588 4.93912C3.87653 4.69632 4.02405 4.47575 4.21 4.29C4.39575 4.10405 4.61632 3.95653 4.85912 3.85588C5.10192 3.75523 5.36217 3.70343 5.625 3.70343C5.88783 3.70343 6.14808 3.75523 6.39088 3.85588C6.63368 3.95653 6.85425 4.10405 7.04 4.29L7.1 4.35C7.33568 4.58054 7.63502 4.73519 7.95941 4.794C8.28381 4.85282 8.61838 4.81312 8.92 4.68H9C9.29577 4.55324 9.54802 4.34276 9.72569 4.07447C9.90337 3.80618 9.99872 3.49179 10 3.17V3C10 2.46957 10.2107 1.96086 10.5858 1.58579C10.9609 1.21071 11.4696 1 12 1C12.5304 1 13.0391 1.21071 13.4142 1.58579C13.7893 1.96086 14 2.46957 14 3V3.09C14.0013 3.41179 14.0966 3.72618 14.2743 3.99447C14.452 4.26276 14.7042 4.47324 15 4.6C15.3016 4.73312 15.6362 4.77282 15.9606 4.714C16.285 4.65519 16.5843 4.50054 16.82 4.27L16.88 4.21C17.0657 4.02405 17.2863 3.87653 17.5291 3.77588C17.7719 3.67523 18.0322 3.62343 18.295 3.62343C18.5578 3.62343 18.8181 3.67523 19.0609 3.77588C19.3037 3.87653 19.5243 4.02405 19.71 4.21C19.896 4.39575 20.0435 4.61632 20.1441 4.85912C20.2448 5.10192 20.2966 5.36217 20.2966 5.625C20.2966 5.88783 20.2448 6.14808 20.1441 6.39088C20.0435 6.63368 19.896 6.85425 19.71 7.04L19.65 7.1C19.4195 7.33568 19.2648 7.63502 19.206 7.95941C19.1472 8.28381 19.1869 8.61838 19.32 8.92V9C19.4468 9.29577 19.6572 9.54802 19.9255 9.72569C20.1938 9.90337 20.5082 9.99872 20.83 10H21C21.5304 10 22.0391 10.2107 22.4142 10.5858C22.7893 10.9609 23 11.4696 23 12C23 12.5304 22.7893 13.0391 22.4142 13.4142C22.0391 13.7893 21.5304 14 21 14H20.91C20.5882 14.0013 20.2738 14.0966 20.0055 14.2743C19.7372 14.452 19.5268 14.7042 19.4 15Z" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
          <button class="toggle-preview-btn" @click="togglePreview">
            <svg viewBox="0 0 24 24" fill="none" class="eye-icon">
              <path d="M1 12S5 4 12 4S23 12 23 12S19 20 12 20S1 12 1 12Z" stroke="currentColor" stroke-width="2"/>
              <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Messages Area -->
      <div class="messages-container" ref="messagesContainer">
        <div v-if="messages.length === 0" class="welcome-screen">
          <div class="welcome-content">
            <div class="logo-section">
              <div class="app-logo">
                <span class="gradient-text">TransformLah</span>
              </div>
              <p class="welcome-subtitle">AI-powered content localization for Malaysia markets</p>
            </div>
            
            <div class="suggestions-grid">
                <div class="suggestion-card" @click="useSuggestion('Translate this English text to Malaysian slang: \'Why didnt you invite me to the party?\'')">
                <div class="suggestion-icon">🌏</div>
                <div class="suggestion-text">Translate to Malaysian slang</div>
              </div>
              <div class="suggestion-card" @click="useSuggestion('Adapt this formal business email for casual Malaysian WhatsApp message')">
                <div class="suggestion-icon">💬</div>
                <div class="suggestion-text">Adapt tone for local audience</div>
              </div>
              <div class="suggestion-card" @click="useSuggestion('Create a social media post for a Malaysian food promotion')">
                <div class="suggestion-icon">🍜</div>
                <div class="suggestion-text">Create localized social content</div>
              </div>
              <div class="suggestion-card" @click="useSuggestion('Convert this product description for Malaysian e-commerce platform')">
                <div class="suggestion-icon">🛒</div>
                <div class="suggestion-text">Localize product descriptions</div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="messages-list">
          <div v-for="message in messages" :key="message.id" class="message-wrapper">
            <div :class="['message', message.role]">
              <div class="message-avatar">
                <div v-if="message.role === 'user'" class="user-avatar">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.89 1 3 1.89 3 3V21C3 22.11 3.89 23 5 23H19C20.11 23 21 22.11 21 21V9M19 9H14V4L19 9Z"/>
                  </svg>
                </div>
                <div v-else class="ai-avatar">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                    <path d="M2 17L12 22L22 17"/>
                    <path d="M2 12L12 17L22 12"/>
                  </svg>
                </div>
              </div>
              <div class="message-content">
                <div class="message-text" v-html="formatMessage(message.content)"></div>
                <div v-if="message.role === 'assistant' && message.content && message.content.type === 'image'" class="image-container">
                  <img :src="'data:image/png;base64,' + message.content.image.source.bytes" style="max-width: 100%; border-radius: 8px; margin: 10px 0;" alt="Generated image" />
                </div>
                <div v-if="message.role === 'assistant' && message.generating" class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area">
        <div class="input-container">
          <textarea
            v-model="inputMessage"
            ref="messageInput"
            placeholder="Describe your content to generate..."
            class="message-input"
            rows="1"
            @keydown.enter.prevent="handleEnter"
            @input="adjustTextareaHeight"
            :disabled="isGenerating"
          ></textarea>
          <button 
            class="send-button" 
            @click="sendMessage" 
            :disabled="!inputMessage.trim() || isGenerating"
          >
            <svg v-if="!isGenerating" viewBox="0 0 24 24" fill="none" class="send-icon">
              <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" stroke="currentColor" stroke-width="2"/>
            </svg>
            <svg v-else class="loading-spinner" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M12 2A10 10 0 0 1 22 12" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
          </button>
        </div>
        <div class="input-footer">
          <p class="disclaimer">TransformLah can make mistakes. Consider checking important information.</p>
        </div>
      </div>
    </div>

    <!-- Preview Section -->
    <div :class="['preview-section', { 'hidden': !showPreview }]">
      <div class="preview-header">
        <h3 class="preview-title">Content Preview</h3>
        <button class="close-preview-btn" @click="togglePreview">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
      </div>
      
      <div class="preview-content">
        <!-- Caption Preview -->
        <div class="preview-section-item">
          <div class="section-header">
            <h4>Caption</h4>
            <div class="section-status" :class="{ active: configuration.type === 'Caption' }">
              {{ configuration.type === 'Caption' ? 'Active' : 'Inactive' }}
            </div>
          </div>
          <div class="section-content">
            <div v-if="previewContents.Caption" class="preview-result">
              <div class="preview-tabs">
                <button 
                  :class="['preview-tab', { 'active': activePreviewTab === 'original' }]"
                  @click="activePreviewTab = 'original'"
                >
                  Original
                </button>
                <button 
                  :class="['preview-tab', { 'active': activePreviewTab === 'transformed' }]"
                  @click="activePreviewTab = 'transformed'"
                >
                  Transformed
                </button>
              </div>
              <div class="preview-display">
                <div v-if="activePreviewTab === 'original'" class="preview-text">
                  {{ previewContents.Caption.original }}
                </div>
                <div v-else>
                  <div class="preview-content-header">
                    <button 
                      v-if="!isEditingCaption" 
                      class="edit-btn"
                      @click="startEditingCaption"
                      title="Edit caption"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" />
                        <path d="M18.5 2.5C18.8978 2.10217 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10217 21.5 2.5C21.8978 2.89782 22.1213 3.43739 22.1213 4C22.1213 4.56261 21.8978 5.10217 21.5 5.5L12 15L8 16L9 12L18.5 2.5Z"/>
                      </svg>
                    </button>
                  </div>
                  <div v-if="isEditingCaption" class="edit-mode">
                    <textarea
                      v-model="editedCaption"
                      class="edit-textarea"
                      rows="4"
                      @input="autoResizeTextarea"
                      ref="editTextarea"
                    ></textarea>
                    <div class="edit-actions">
                      <button class="save-edit-btn" @click="saveEditedCaption">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M5 13L9 17L19 7"/>
                        </svg>
                        Save
                      </button>
                      <button class="cancel-edit-btn" @click="cancelEditingCaption">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M6 18L18 6M6 6L18 18"/>
                        </svg>
                        Cancel
                      </button>
                    </div>
                  </div>
                  <div v-else class="preview-text">
                    {{ previewContents.Caption.transformed }}
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <p>{{ configuration.type === 'Caption' ? 'Enter your prompt to generate a caption' : 'No caption generated yet' }}</p>
            </div>
          </div>
        </div>

        <!-- Image Preview -->
        <div class="preview-section-item">
          <div class="section-header">
            <h4>Image</h4>
            <div class="section-status" :class="{ active: configuration.type === 'Image' }">
              {{ configuration.type === 'Image' ? 'Active' : 'Inactive' }}
            </div>
          </div>
          <div class="section-content">
            <div v-if="previewContents.Image && previewContents.Image.imageData" class="preview-result">
              <div class="preview-tabs">
                <button 
                  :class="['preview-tab', { 'active': activePreviewTab === 'original' }]"
                  @click="activePreviewTab = 'original'"
                >
                  Prompt
                </button>
                <button 
                  :class="['preview-tab', { 'active': activePreviewTab === 'transformed' }]"
                  @click="activePreviewTab = 'transformed'"
                >
                  Generated
                </button>
              </div>
              <div class="preview-display">
                <div v-if="activePreviewTab === 'original'" class="preview-text">
                  {{ previewContents.Image.original }}
                </div>
                <div v-else class="preview-image">
                  <img 
                    :src="'data:image/png;base64,' + previewContents.Image.imageData" 
                    style="max-width: 100%; border-radius: 8px;" 
                    alt="Generated image" 
                  />
                  <div class="image-details">
                    <p class="preview-text">{{ previewContents.Image.transformed }}</p>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <p>{{ configuration.type === 'Image' ? 'Enter your prompt to generate an image' : 'No image generated yet' }}</p>
            </div>
          </div>
        </div>

        <!-- Video Preview -->
        <div class="preview-section-item">
          <div class="section-header">
            <h4>Video</h4>
            <div class="section-status" :class="{ active: configuration.type === 'Video' }">
              {{ configuration.type === 'Video' ? 'Active' : 'Inactive' }}
            </div>
          </div>
          <div class="section-content">
            <div v-if="previewContents.Video" class="preview-result">
              <div class="preview-tabs">
                <button 
                  :class="['preview-tab', { 'active': activePreviewTab === 'original' }]"
                  @click="activePreviewTab = 'original'"
                >
                  Prompt
                </button>
                <button 
                  :class="['preview-tab', { 'active': activePreviewTab === 'transformed' }]"
                  @click="activePreviewTab = 'transformed'"
                >
                  Generated
                </button>
              </div>
              <div class="preview-display">
                <div v-if="activePreviewTab === 'original'" class="preview-text">
                  {{ previewContents.Video.original }}
                </div>
                <div v-else class="preview-text">
                  {{ previewContents.Video.transformed }}
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <p>{{ configuration.type === 'Video' ? 'Enter your prompt to generate a video' : 'No video generated yet' }}</p>
            </div>
          </div>
        </div>

        <!-- Preview Actions -->
        <div class="preview-actions">
          <button class="preview-action-btn" @click="copyToClipboard(previewContent.transformed)">
            <svg viewBox="0 0 24 24" fill="none">
              <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2"/>
              <path d="M5 15H4C3.46957 15 2.96086 14.7893 2.58579 14.4142C2.21071 14.0391 2 13.5304 2 13V4C2 3.46957 2.21071 2.96086 2.58579 2.58579C2.96086 2.21071 3.46957 2 4 2H13C13.5304 2 14.0391 2.21071 14.4142 2.58579C14.7893 2.96086 15 3.46957 15 4V5" stroke="currentColor" stroke-width="2"/>
            </svg>
            Copy
          </button>
          <button class="preview-action-btn" @click="downloadContent">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15M12 15L17 10M12 15V3" stroke="currentColor" stroke-width="2"/>
            </svg>
            Download
          </button>
          <div class="share-dropdown-container">
            <button 
              class="preview-action-btn share-btn" 
              @click="toggleShareDropdown"
              :disabled="isPosting || !previewContents.Image || !previewContents.Caption"
            >
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M16 8.5L8 13.5M16 15.5L8 10.5M15 7C16.1046 7 17 6.10457 17 5C17 3.89543 16.1046 3 15 3C13.8954 3 13 3.89543 13 5C13 6.10457 13.8954 7 15 7ZM7 12C8.10457 12 9 11.1046 9 10C9 8.89543 8.10457 8 7 8C5.89543 8 5 8.89543 5 10C5 11.1046 5.89543 12 7 12ZM15 21C16.1046 21 17 20.1046 17 19C17 17.8954 16.1046 17 15 17C13.8954 17 13 17.8954 13 19C13 20.1046 13.8954 21 15 21Z" stroke="currentColor" stroke-width="2"/>
              </svg>
              {{ isPosting ? 'Posting...' : 'Share' }}
            </button>
            <div v-if="showShareDropdown" class="share-dropdown">
              <button 
                class="share-option" 
                @click="postToSocialMedia('instagram')"
                :disabled="isPosting"
              >
                <svg viewBox="0 0 24 24" fill="none">
                  <rect x="2" y="2" width="20" height="20" rx="4" stroke="currentColor" stroke-width="2"/>
                  <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2"/>
                  <circle cx="18" cy="6" r="1.5" fill="currentColor"/>
                </svg>
                Instagram
              </button>
              <button 
                class="share-option" 
                @click="postToSocialMedia('facebook')"
                :disabled="isPosting"
              >
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M18 2H15C13.6739 2 12.4021 2.52678 11.4645 3.46447C10.5268 4.40215 10 5.67392 10 7V10H7V14H10V22H14V14H17L18 10H14V7C14 6.73478 14.1054 6.48043 14.2929 6.29289C14.4804 6.10536 14.7348 6 15 6H18V2Z" stroke="currentColor" stroke-width="2"/>
                </svg>
                Facebook
              </button>
              <button 
                class="share-option" 
                @click="postToSocialMedia('youtube')"
                :disabled="isPosting"
              >
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M22.54 6.42C22.4212 5.94541 22.1793 5.51057 21.8387 5.15941C21.498 4.80824 21.0708 4.55318 20.6 4.42C18.88 4 12 4 12 4C12 4 5.12 4 3.4 4.46C2.92925 4.59318 2.50198 4.84824 2.16134 5.19941C1.82069 5.55057 1.57878 5.98541 1.46 6.46C1.14521 8.20556 0.991235 9.97631 0.999999 11.75C0.988779 13.537 1.14276 15.3213 1.46 17.08C1.59096 17.5398 1.83831 17.9581 2.17814 18.2945C2.51798 18.6308 2.93882 18.8738 3.4 19C5.12 19.46 12 19.46 12 19.46C12 19.46 18.88 19.46 20.6 19C21.0708 18.8668 21.498 18.6118 21.8387 18.2606C22.1793 17.9094 22.4212 17.4746 22.54 17C22.8524 15.2676 23.0063 13.5103 23 11.75C23.0112 9.96295 22.8572 8.1787 22.54 6.42Z" stroke="currentColor" stroke-width="2"/>
                  <path d="M9.75 15.02L15.5 11.75L9.75 8.48001V15.02Z" stroke="currentColor" stroke-width="2"/>
                </svg>
                YouTube
              </button>
              <button 
                class="share-option" 
                @click="postToSocialMedia('tiktok')"
                :disabled="isPosting"
              >
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M16.6 5C16.4 5.3 16.2 5.7 16.1 6C15.8 6.7 15.6 7.5 15.6 8.3V9.7C15.6 9.9 15.5 10 15.3 10C15.1 10 15 9.9 15 9.7V8.3C15 6.5 15.9 4.9 17.3 4C17.5 3.9 17.7 3.9 17.9 4C18 4.2 18 4.4 17.8 4.6C17.4 4.8 17 4.9 16.6 5ZM21 14.5C21 15.9 19.9 17 18.5 17C17.1 17 16 15.9 16 14.5C16 13.1 17.1 12 18.5 12C19.9 12 21 13.1 21 14.5ZM3 14.5C3 15.9 4.1 17 5.5 17C6.9 17 8 15.9 8 14.5C8 13.1 6.9 12 5.5 12C4.1 12 3 13.1 3 14.5Z" stroke="currentColor" stroke-width="2"/>
                </svg>
                TikTok
              </button>
              <button 
                class="share-option" 
                @click="postToSocialMedia('linkedin')"
                :disabled="isPosting"
              >
                <svg viewBox="0 0 24 24" fill="none">
                  <rect x="2" y="2" width="20" height="20" rx="2" stroke="currentColor" stroke-width="2"/>
                  <path d="M8 10V16M8 7V7.01M16 16V12C16 10.8954 15.1046 10 14 10C12.8954 10 12 10.8954 12 12V16M12 10V16" stroke="currentColor" stroke-width="2"/>
                </svg>
                LinkedIn
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>    <!-- Settings Modal -->
    <div v-if="showSettings" class="settings-modal">
      <div class="settings-modal-content">
        <div class="modal-header">
          <h2>Content Configuration</h2>
          <button class="close-modal-btn" @click="toggleSettings">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M6 18L18 6M6 6L18 18" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <!-- Content Type -->
          <div class="form-group">
            <label>Content Type <span class="required">*</span></label>
            <select v-model="configuration.type" required>
              <option value="Caption">Caption</option>
              <option value="Image">Image</option>
              <option value="Video">Video</option>
            </select>
          </div>

          <!-- Common Fields -->
          <div class="form-section">
            <h3>Common Fields</h3>
            <div class="form-group">
              <label>Brand Name</label>
              <input type="text" v-model="configuration.brand_name" placeholder="Enter brand name">
            </div>

            <div class="form-group">
              <label>Campaign Details</label>
              <textarea v-model="configuration.campaign_details" placeholder="Enter campaign details"></textarea>
            </div>

            <div class="form-group">
              <label>Target Race</label>
              <select v-model="configuration.target_race">
                <option value="">Select target race</option>
                <option value="Malay">Malay</option>
                <option value="Chinese">Chinese</option>
                <option value="Indian">Indian</option>
                <option value="All">All</option>
              </select>
            </div>

            <div class="form-group">
              <label>Target Audience</label>
              <select v-model="configuration.target_audience">
                <option value="">Select target audience</option>
                <option value="Gen Z">Gen Z</option>
                <option value="Millennials">Millennials</option>
                <option value="Gen X">Gen X</option>
                <option value="Boomers">Boomers</option>
                <option value="All">All Ages</option>
              </select>
            </div>
          </div>

          <!-- Content Type Specific Fields -->
          <div v-if="configuration.type === 'Caption'" class="form-section">
            <h3>Caption Settings</h3>
                   <div class="form-group">
              <label>Tone / Mood</label>
              <select v-model="configuration.tone">
                <option value="">Select tone</option>
                <option value="Festive">Festive</option>
                <option value="Joyful">Joyful</option>
                <option value="Casual">Casual</option>
                <option value="Professional">Professional</option>
                <option value="Marketing">Marketing</option>
                <option value="Trendy">Trendy</option>
                <option value="Educational">Educational</option>
                <option value="Warm">Warm</option>
                <option value="Humorous">Humorous</option>
              </select>
            </div>
            <div class="form-group">
              <label>Language</label>
              <select v-model="configuration.language">
                <option value="">Select language</option>
                <option value="English">English</option>
                <option value="Bahasa Malaysia">Bahasa Malaysia</option>
                <option value="Mandarin">Mandarin</option>
              </select>
            </div>
            <div class="form-group">
              <label>Platform</label>
              <select v-model="configuration.platform">
                <option value="">Select platform</option>
                <option value="Instagram">Instagram</option>
                <option value="Facebook">Facebook</option>
                <option value="Twitter">Twitter</option>
                <option value="LinkedIn">LinkedIn</option>
                <option value="TikTok">TikTok</option>
              </select>
            </div>
            <div class="form-group">
              <label>Length</label>
              <select v-model="configuration.length">
                <option value="<30 words">Less than 30 words</option>
                <option value="30 - 60 words">30 - 60 words</option>
                <option value="60 - 100 words">60 - 100 words</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            <div class="form-group">
              <label>Include Emojis</label>
              <select v-model="configuration.include_emojis">
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>
            <div class="form-group">
              <label>Number of Hashtags</label>
              <select v-model="configuration.hashtag_count">
                <option value="none">No hashtags</option>
                <option value="3">3 hashtags</option>
                <option value="5">5 hashtags</option>
                <option value="10">10 hashtags</option>
              </select>
            </div>
          </div>

          <div v-if="configuration.type === 'Image'" class="form-section">
            <h3>Image Settings</h3>
              <div class="form-group">
              <label>Reference Image (Optional)</label>
              <div class="image-upload-container">
                <input 
                  type="file" 
                  ref="imageUpload"
                  @change="handleImageUpload" 
                  accept="image/*"
                  class="image-upload-input"
                  id="image-upload"
                >
                <label for="image-upload" class="image-upload-label">
                  <svg viewBox="0 0 24 24" fill="none" class="upload-icon">
                    <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M17 8L12 3M12 3L7 8M12 3V15" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <span v-if="!uploadedImage">Choose reference image</span>
                  <span v-else>{{ uploadedImage.name }}</span>
                </label>
                <button 
                  v-if="uploadedImage" 
                  @click="clearUploadedImage"
                  class="clear-image-btn"
                  type="button"
                >
                  <svg viewBox="0 0 24 24" fill="none">
                    <path d="M6 18L18 6M6 6L18 18" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </button>
              </div>
              <div v-if="uploadedImage" class="image-preview">
                <img :src="uploadedImagePreview" alt="Preview" class="preview-img">
                <div class="image-info">
                  <p><strong>{{ uploadedImage.name }}</strong></p>
                  <p>{{ formatFileSize(uploadedImage.size) }} - {{ uploadedImageDimensions }}</p>
                </div>
              </div>
              <p class="upload-help">Upload a reference image to guide the generation. Supports JPEG, PNG (max 20MB, max 4.2M pixels)</p>
            </div>
            <div class="form-group">
              <label>Color Palette</label>
              <input type="text" v-model="configuration.color_palette" placeholder="Enter color palette preferences">
            </div>
            <div class="form-group">
              <label>Image Size</label>
              <select v-model="configuration.image_size">
                <option value="">Select image size</option>
                <option value="square_1080">Instagram Square (1080x1080)</option>
                <option value="portrait_1080">Instagram Portrait (1080x1350)</option>
                <option value="story_1080">Instagram Story (1080x1920)</option>
                <option value="fb_cover">Facebook Cover (820x312)</option>
                <option value="fb_post">Facebook Post (1200x630)</option>
                <option value="twitter_post">Twitter Post (1200x675)</option>
                <option value="linkedin_post">LinkedIn Post (1200x627)</option>
                <option value="tiktok_video">TikTok Cover (1080x1920)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Background Style</label>
              <select v-model="configuration.background_style">
                <option value="">Select background style</option>
                <option value="solid">Solid Color</option>
                <option value="gradient">Gradient</option>
                <option value="pattern">Pattern</option>
                <option value="transparent">Transparent</option>
                <option value="scene">Scene/Environment</option>
              </select>
            </div>
          </div>

          <div v-if="configuration.type === 'Video'" class="form-section">
            <h3>Video Settings</h3>
            <div class="form-group">
              <label>Duration</label>
              <select v-model="configuration.duration">
                <option value="10s">10 seconds</option>
                <option value="30s">30 seconds</option>
                <option value="60s">60 seconds</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="save-btn" @click="saveConfiguration">Save Configuration</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const BACKEND_LOCAL_HOST_ENV = 'http://127.0.0.1:8000';

export default {
  name: 'GeneratorPage',
  
  mounted() {
    // Add click outside handler for share dropdown
    document.addEventListener('click', this.handleClickOutside);
  },

  beforeUnmount() {
    // Remove click outside handler when component is destroyed
    document.removeEventListener('click', this.handleClickOutside);
  },
  
  data() {
    return {
      messages: [],
      inputMessage: '',
      isGenerating: false,
      isPosting: false,
      postError: null,
      showShareDropdown: false,
      showPreview: true,
      previewContents: {
        Caption: null,
        Image: null,
        Video: null
      },
      activePreviewTab: 'transformed',
      isSidebarCollapsed: false,
      searchQuery: '',
      showSettings: false,
      configuration: {
        type: 'Caption',
        brand_name: '',
        campaign_details: '',
        target_race: '',
        tone: '',
        language: '',
        length: '',
        color_palette: '',
        duration: '',
        include_emojis: 'yes',
        hashtag_count: '3',
        platform: '',
        target_audience: '',
        image_size: '',
        background_style: 'standard',
        image_aspect_ratio: '1:1',
        image_dimensions: {
          width: 0,
          height: 0
        }
      },
      chatHistory: [
        { id: 1, title: 'Localizing Product Description', date: '2025-09-20' },
        { id: 2, title: 'Malaysian Slang Translation', date: '2025-09-19' },
        { id: 3, title: 'Social Media Campaign', date: '2025-09-18' },
        { id: 4, title: 'WhatsApp Message Adaptation', date: '2025-09-17' }
      ],
      currentChatId: null,
      isEditingCaption: false,
      editedCaption: '',
      sessionId: null
    }
  },
  computed: {
    filteredChatHistory() {
      if (!this.searchQuery) return this.chatHistory
      const query = this.searchQuery.toLowerCase()
      return this.chatHistory.filter(chat => 
        chat.title.toLowerCase().includes(query)
      )
    }
  },
  methods: {
    toggleShareDropdown() {
      if (!this.isPosting && this.previewContents.Image && this.previewContents.Caption) {
        this.showShareDropdown = !this.showShareDropdown;
      }
    },

    closeShareDropdown() {
      this.showShareDropdown = false;
    },

    async postToSocialMedia(platform) {
      if (!this.previewContents.Image || !this.previewContents.Caption) {
        alert('Both caption and image are required to post');
        return;
      }

      let tempImageUrl = null;
      let tempFilename = null;

      try {
        this.isPosting = true;
        this.postError = null;
        this.showShareDropdown = false;
        
        const imageBase64 = this.previewContents.Image.imageData;
        const caption = this.previewContents.Caption.transformed;

        // Step 1: Convert base64 to temporary URL
        const uploadResponse = await fetch(`${BACKEND_LOCAL_HOST_ENV}/upload/temp-image`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image_base64: imageBase64
          }),
        });

        if (!uploadResponse.ok) {
          throw new Error('Failed to create temporary image URL');
        }

        const uploadResult = await uploadResponse.json();
        tempImageUrl = uploadResult.image_url;
        tempFilename = uploadResult.temp_filename;

        // Step 2: Post to social media using the temporary URL
        let endpoint = '';
        switch (platform) {
          case 'instagram':
            endpoint = '/social/instagram/post';
            break;
          case 'facebook':
            endpoint = '/social/facebook/post';
            break;
          case 'youtube':
            endpoint = '/social/youtube/post';
            break;
          case 'tiktok':
            endpoint = '/social/tiktok/post';
            break;
          case 'linkedin':
            endpoint = '/social/linkedin/post';
            break;
          default:
            throw new Error('Unsupported platform');
        }
        
        const postResponse = await fetch(`${BACKEND_LOCAL_HOST_ENV}${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            caption: caption,
            image_url: tempImageUrl
          }),
        });

        if (!postResponse.ok) {
          const errorData = await postResponse.json().catch(() => null);
          const errorMessage = errorData?.detail || `HTTP ${postResponse.status}`;
          throw new Error(`Failed to post to ${platform}: ${errorMessage}`);
        }

        const result = await postResponse.json();
        
        if (result.success) {
          alert(`Successfully posted to ${platform}!`);
        } else {
          throw new Error(result.message || `Failed to post to ${platform}`);
        }

      } catch (error) {
        this.postError = error.message;
        alert(`Error posting to ${platform}: ${error.message}`);
        console.error('Post error:', error);
      } finally {
        this.isPosting = false;
        
        // Step 3: Clean up temporary image file
        if (tempFilename) {
          try {
            await fetch(`${BACKEND_LOCAL_HOST_ENV}/upload/temp-image/${tempFilename}`, {
              method: 'DELETE'
            });
          } catch (cleanupError) {
            console.warn('Failed to clean up temporary file:', cleanupError);
          }
        }
      }
    },

    startNewChat() {
      this.messages = []
      this.previewContents = {
        Caption: null,
        Image: null,
        Video: null
      }
      this.inputMessage = ''
      this.currentChatId = null
      this.sessionId = crypto.randomUUID();
    },
    
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed
    },

    loadChat(chatId) {
      this.currentChatId = chatId
      // Mock loading chat messages - in real app, fetch from backend
      const chat = this.chatHistory.find(c => c.id === chatId)
      if (chat) {
        this.messages = [
          {
            id: Date.now(),
            role: 'user',
            content: `Load conversation about ${chat.title}`
          },
          {
            id: Date.now() + 1,
            role: 'assistant',
            content: `This is a mock conversation about ${chat.title}. In a real application, this would load the actual chat history from your backend.`
          }
        ]
      }
    },

    deleteChat(chatId) {
      const index = this.chatHistory.findIndex(c => c.id === chatId)
      if (index !== -1) {
        this.chatHistory.splice(index, 1)
        if (this.currentChatId === chatId) {
          this.startNewChat()
        }
      }
    },
    
    togglePreview() {
      this.showPreview = !this.showPreview
    },
    
    useSuggestion(suggestion) {
      this.inputMessage = suggestion
      this.sendMessage()
    },
    
    handleEnter(event) {
      if (event.shiftKey) {
        return // Allow line break with Shift+Enter
      }
      this.sendMessage()
    },
    
    adjustTextareaHeight() {
      this.$nextTick(() => {
        const textarea = this.$refs.messageInput
        textarea.style.height = 'auto'
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'
      })
    },
    
    toggleSettings() {
      this.showSettings = !this.showSettings;
    },

    saveConfiguration() {
      this.showSettings = false;
      // Update image dimensions based on selected image size
      // Ensure dimensions are within Nova Canvas limits (64x64 to 2048x2048)
      if (this.configuration.type === 'Image') {
        // Handle uploaded image if available
        if (this.uploadedImage) {
          this.configuration.customImage = this.uploadedImage;
        }
        
        switch (this.configuration.image_size) {
          case 'square_1080':
            this.configuration.image_dimensions = { width: 1024, height: 1024 };
            this.configuration.image_aspect_ratio = '1:1';
            break;
          case 'portrait_1080':
            this.configuration.image_dimensions = { width: 1024, height: 1280 };
            this.configuration.image_aspect_ratio = '4:5';
            break;
          case 'story_1080':
            this.configuration.image_dimensions = { width: 1024, height: 1824 };
            this.configuration.image_aspect_ratio = '9:16';
            break;
          case 'fb_cover':
            this.configuration.image_dimensions = { width: 820, height: 312 };
            this.configuration.image_aspect_ratio = '2.63:1';
            break;
          case 'fb_post':
            this.configuration.image_dimensions = { width: 1200, height: 630 };
            this.configuration.image_aspect_ratio = '1.91:1';
            break;
          case 'twitter_post':
            this.configuration.image_dimensions = { width: 1200, height: 675 };
            this.configuration.image_aspect_ratio = '16:9';
            break;
          case 'linkedin_post':
            this.configuration.image_dimensions = { width: 1200, height: 627 };
            this.configuration.image_aspect_ratio = '1.91:1';
            break;
          case 'tiktok_video':
            this.configuration.image_dimensions = { width: 1024, height: 1824 };
            this.configuration.image_aspect_ratio = '9:16';
            break;
        }
        
        // Ensure dimensions are within Nova Canvas limits
        if (this.configuration.image_dimensions) {
          const maxDim = 2048;
          const minDim = 64;
          
          let { width, height } = this.configuration.image_dimensions;
          
          // Enforce maximum dimensions while maintaining aspect ratio
          if (width > maxDim || height > maxDim) {
            const aspectRatio = width / height;
            if (width > height) {
              width = maxDim;
              height = Math.round(width / aspectRatio);
            } else {
              height = maxDim;
              width = Math.round(height * aspectRatio);
            }
          }
          
          // Enforce minimum dimensions while maintaining aspect ratio
          if (width < minDim || height < minDim) {
            const aspectRatio = width / height;
            if (width < height) {
              width = minDim;
              height = Math.round(width / aspectRatio);
            } else {
              height = minDim;
              width = Math.round(height * aspectRatio);
            }
          }
          
          // Update dimensions with validated values
          this.configuration.image_dimensions = {
            width: Math.max(minDim, Math.min(maxDim, Math.round(width))),
            height: Math.max(minDim, Math.min(maxDim, Math.round(height)))
          };
        }
      }
    },

    async fetchLatestImage() {
      try {
        const response = await fetch(`${BACKEND_LOCAL_HOST_ENV}/api/latest-image`);
        if (response.ok) {
          const data = await response.json();
          const imageUrl = `${BACKEND_LOCAL_HOST_ENV}${data.path}`;
          
          // Store the complete image data in the message
          const lastMessage = this.messages[this.messages.length - 1];
          if (lastMessage) {
            lastMessage.content = {
              type: 'image',
              imageUrl
            };
          }
          
          // Update preview content
          this.previewContent = {
            original: this.previewContent?.original || '',
            transformed: `Generated image: ${lastMessage?.metadata?.dimensions || 'Unknown size'}`,
            imageUrl
          };
        }
      } catch (error) {
        console.error('Failed to fetch latest image:', error);
      }
    },

    async sendMessage() {
      console.log('1. inputMessage:', this.inputMessage);
      const trimmedInput = this.inputMessage.trim();
      console.log('2. trimmedInput:', trimmedInput);

      if (!trimmedInput || this.isGenerating) {
        console.log('3. returning early');
        return;
      }
      
      if (!this.configuration.type) {
        alert('Please configure content type in settings first');
        this.toggleSettings();
        return;
      }

      if (!this.sessionId) {
        this.startNewChat();
      }

      const userMessage = {
        id: Date.now(),
        role: 'user',
        content: trimmedInput
      }
      
      console.log('4. userMessage:', userMessage);
      this.messages.push(userMessage);
      console.log('5. messages array:', this.messages);
      console.log('session_id:', this.sessionId);

      const originalInput = this.inputMessage;
      this.inputMessage = ''
      this.isGenerating = true
      
      // Add assistant message with typing indicator
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '',
        generating: true
      }
      
      this.messages.push(assistantMessage)
      this.scrollToBottom()
      
      try {
        // Create FormData
        const formData = new FormData();
        formData.append('prompt', trimmedInput);
        console.log('6. formData prompt:', trimmedInput);
        formData.append('configuration', JSON.stringify(this.configuration));
        formData.append('session_id', this.sessionId);

        // Determine endpoint based on content type
        let endpoint;
        switch (this.configuration.type) {
          case 'Caption':
            endpoint = '/generate/caption';
            break;
          case 'Image':
            endpoint = '/generate/image';
            break;
          case 'Video':
            endpoint = '/generate/video';
            break;
          default:
            throw new Error('Unsupported content type');
        }

        // Call the backend API with SSE
        const response = await fetch(`${BACKEND_LOCAL_HOST_ENV}${endpoint}`, {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error('Failed to generate content');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedText = '';
        let buffer = ''; // Add buffer to accumulate incomplete chunks
        let isStreaming = true;

        while (isStreaming) {
          const { value, done } = await reader.read();
          if (done) {
            isStreaming = false;
            break;
          }

          // Decode the chunk and add to buffer
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;
          
          // Split by lines and process complete lines
          const lines = buffer.split('\n');
          
          // Keep the last line in buffer (might be incomplete)
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.trim().startsWith('data:')) {
              try {
                const jsonStr = line.slice(5).trim(); // Remove 'data: ' prefix
                if (jsonStr === '[DONE]') {
                  isStreaming = false;
                  break;
                }

                // Skip empty data lines
                if (!jsonStr) continue;

                const data = JSON.parse(jsonStr);
                
                if (data.type === 'chunk' && data.text) {
                  // Accumulate the text chunks
                  accumulatedText += data.text;
                  // Update the message content in real-time
                  assistantMessage.content = accumulatedText;
                  this.scrollToBottom();
                } else if (data.type === 'image') {
                  console.log('Received image data:', {
                    hasImageData: !!data.image,
                    hasBytes: !!(data.image && data.image.source && data.image.source.bytes),
                    metadata: data.metadata
                  });
                  
                  // Handle image display directly without additional fetch
                  if (data.image && data.image.source && data.image.source.bytes) {
                    assistantMessage.content = {
                      type: 'image',
                      image: data.image
                    };
                    
                    // Update preview content for images
                    let dimensions;
                    if (this.configuration.image_dimensions) {
                      dimensions = `${this.configuration.image_dimensions.width}x${this.configuration.image_dimensions.height}`;
                    } else if (data.metadata && data.metadata.width && data.metadata.height) {
                      dimensions = `${data.metadata.width}x${data.metadata.height}`;
                    } else {
                      dimensions = 'standard size';
                    }

                    // Store in the correct preview type
                    this.previewContents.Image = {
                      original: originalInput,
                      transformed: `Generated image (${dimensions})`,
                      imageData: data.image.source.bytes
                    };
                  }
                  
                  assistantMessage.generating = false;
                  this.scrollToBottom();
                } else if (data.type === 'stop') {
                  // Handle completion
                  assistantMessage.generating = false;
                  this.isGenerating = false;
                  
                  if (accumulatedText && !assistantMessage.content.type) {
                    // Store in the correct preview type based on configuration
                    this.previewContents[this.configuration.type] = {
                      original: originalInput,
                      transformed: accumulatedText
                    };
                  }
                  isStreaming = false;
                }
              } catch (e) {
                console.warn('Failed to parse SSE data:', e, 'Line:', line);
                // Continue processing other lines even if one fails
              }
            }
          }
        }

        this.scrollToBottom();
      } catch (error) {
        console.error('Error generating content:', error);
        assistantMessage.content = 'Sorry, there was an error generating the content. Please try again.'
        assistantMessage.generating = false
        this.isGenerating = false
        this.scrollToBottom()
      }
    },
    
    generateResponse(input) {
      // Mock response generation
      const responses = [
        "Here's your content localized for Malaysian audience:\n\n**Original**: " + input + "\n\n**Malaysian Version**: " + this.mockTransform(input),
        "I've adapted your content for Malaysian market preferences. The localized version maintains your brand voice while incorporating local cultural nuances.",
        "Content successfully transformed! Here's the Malaysian-friendly version that resonates with local audiences."
      ]
      
      return responses[Math.floor(Math.random() * responses.length)]
    },
    
    mockTransform(text) {
      // Simple mock transformation
      return text
        .replace(/Why didn't you invite me/gi, "Bojio")
        .replace(/party/gi, "makan-makan")
        .replace(/awesome/gi, "syok")
        .replace(/cool/gi, "best")
        .replace(/great/gi, "power")
    },
    
    // Also update your formatMessage method to handle the image data correctly:
    formatMessage(content) {
      try {
        // Only handle text content here
        if (typeof content === 'string') {
          return content.replace(/\n/g, '<br>')
        }
        // For any other content type (including images), return empty string
        // as they will be handled by their dedicated containers
        return ''
      } catch (error) {
        console.error('Error formatting message:', error)
        return ''
      }
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        container.scrollTop = container.scrollHeight
      })
    },
    
    copyToClipboard() {
      const activeContent = this.previewContents[this.configuration.type];
      if (!activeContent) return;
      
      const textToCopy = activeContent.transformed;
      navigator.clipboard.writeText(textToCopy).then(() => {
        // Could add toast notification here
        console.log('Copied to clipboard')
      })
    },
    
    downloadContent() {
      const activeContent = this.previewContents[this.configuration.type];
      if (!activeContent) return;
      
      if (this.configuration.type === 'Image' && activeContent.imageData) {
        // Download image
        const a = document.createElement('a');
        a.href = 'data:image/png;base64,' + activeContent.imageData;
        a.download = 'generated-image.png';
        a.click();
      } else {
        // Download text content
        const content = `Original: ${activeContent.original}\n\nTransformed: ${activeContent.transformed}`;
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transformed-${this.configuration.type.toLowerCase()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
      }
    },

    startEditingCaption() {
      if (this.previewContents.Caption) {
        this.editedCaption = this.previewContents.Caption.transformed;
        this.isEditingCaption = true;
        this.$nextTick(() => {
          if (this.$refs.editTextarea) {
            this.$refs.editTextarea.focus();
            this.autoResizeTextarea();
          }
        });
      }
    },

    saveEditedCaption() {
      if (this.previewContents.Caption) {
        this.previewContents.Caption.transformed = this.editedCaption;
        this.isEditingCaption = false;
      }
    },

    cancelEditingCaption() {
      this.isEditingCaption = false;
      this.editedCaption = '';
    },

    autoResizeTextarea() {
      const textarea = this.$refs.editTextarea;
      if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
      }
    }
  }
}
</script>

<style scoped>
.generator-container {
  display: flex;
  height: 100vh;
  background: #f7f7f8;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background: white;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  border-right: 1px solid #e5e5e5;
}

.sidebar.collapsed {
  width: 0;
  overflow: hidden;
}

.sidebar-header {
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e5e5e5;
  background: white;
}

.collapse-btn {
  background: none;
  border: none;
  color: #6b7280;
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.collapse-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.collapse-btn svg {
  width: 16px;
  height: 16px;
}

.search-container {
  padding: 0.75rem;
  border-bottom: 1px solid #e5e5e5;
  background: white;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  width: 16px;
  height: 16px;
  color: #6b7280;
}

.search-input {
  width: 100%;
  background: #f3f4f6;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  padding: 0.5rem 0.75rem 0.5rem 2.25rem;
  color: #374151;
  font-size: 0.875rem;
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  background: white;
}

.chat-history-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  color: #374151;
  transition: all 0.2s ease;
  position: relative;
}

.chat-history-item:hover {
  background: #f3f4f6;
}

.chat-history-item.active {
  background: #eef2ff;
  color: #667eea;
}

.chat-icon {
  width: 18px;
  height: 18px;
  color: #9ca3af;
}

.chat-title {
  flex: 1;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.delete-chat-btn {
  display: none;
  background: none;
  border: none;
  padding: 0.25rem;
  color: #9ca3af;
  cursor: pointer;
  border-radius: 4px;
}

.chat-history-item:hover .delete-chat-btn {
  display: block;
}

.delete-chat-btn:hover {
  background: #f3f4f6;
  color: #ef4444;
}

.delete-chat-btn svg {
  width: 14px;
  height: 14px;
}

.expand-sidebar-btn {
  background: none;
  border: none;
  color: #6b7280;
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.expand-sidebar-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.expand-sidebar-btn svg {
  width: 18px;
  height: 18px;
}

/* Chat Section */
.chat-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-right: 1px solid #e5e5e5;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e5e5;
  background: white;
  position: sticky;
  top: 0;
  z-index: 10;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #10a37f;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.new-chat-btn:hover {
  background: #0d8c6c;
}

.plus-icon {
  width: 16px;
  height: 16px;
}

.chat-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #0d1117;
  margin: 0;
}

.gradient-text {
  color: #667eea;
  font-weight: 800;
}

.toggle-preview-btn {
  background: none;
  border: 1px solid #e5e5e5;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-preview-btn:hover {
  background: #f5f5f5;
}

.eye-icon {
  width: 18px;
  height: 18px;
  color: #6b7280;
}

/* Messages Container */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.welcome-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
}

.welcome-content {
  text-align: center;
  max-width: 600px;
}

.logo-section {
  margin-bottom: 3rem;
}

.app-logo {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 1rem;
}

.welcome-subtitle {
  color: #6b7280;
  font-size: 1.125rem;
  margin: 0;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.suggestion-card {
  background: white;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.suggestion-card:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.suggestion-icon {
  font-size: 1.5rem;
  margin-bottom: 0.75rem;
}

.suggestion-text {
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Messages List */
.messages-list {
  padding: 1rem 0;
}

.message-wrapper {
  margin-bottom: 1.5rem;
}

.message {
  display: flex;
  gap: 1rem;
  padding: 0 1.5rem;
}

.message.user {
  background: #f7f7f8;
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;
}

.message.assistant {
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-avatar {
  background: #10a37f;
  color: white;
}

.user-avatar svg {
  width: 18px;
  height: 18px;
}

.ai-avatar {
  background: #667eea;
  color: white;
}

.ai-avatar svg {
  width: 16px;
  height: 16px;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-text {
  color: #374151;
  line-height: 1.6;
  font-size: 0.975rem;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 0.5rem;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: #9ca3af;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; }
  30% { opacity: 1; }
}

/* Input Area */
.input-area {
  border-top: 1px solid #e5e5e5;
  background: white;
  padding: 0.5rem 1rem; /* reduced from 1rem 1.5rem */
}

.input-container {
  position: relative;
  background: white;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 0.5rem; /* reduced from 1rem */
  display: flex;
  align-items: flex-end;
  gap: 0.5rem; /* optional: slightly reduce gap */
}


.input-container:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.message-input {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-size: 1rem;
  line-height: 1.5;
  background: transparent;
  min-height: 24px;
  max-height: 200px;
  font-family: inherit;
}

.message-input::placeholder {
  color: #9ca3af;
}

.send-button {
  width: 32px;
  height: 32px;
  background: #10a37f;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background: #0d8c6c;
}

.send-button:disabled {
  background: #e5e7eb;
  cursor: not-allowed;
}

.send-icon, .loading-spinner {
  width: 16px;
  height: 16px;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.input-footer {
  text-align: center;
  margin-top: 0.75rem;
}

.disclaimer {
  color: #9ca3af;
  font-size: 0.75rem;
  margin: 0;
}

/* Preview Section */
.preview-section {
  width: 25%;
  background: #f7f7f8;
  border-left: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.preview-section.hidden {
  width: 0;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e5e5;
  background: white;
}

.preview-title {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.close-preview-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: #6b7280;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-preview-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.close-preview-btn svg {
  width: 16px;
  height: 16px;
}

.preview-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.preview-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.preview-result {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.preview-tabs {
  display: flex;
  border-bottom: 1px solid #e5e5e5;
  background: white;
}

.preview-tab {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 2px solid transparent;
}

.preview-tab.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.preview-tab:hover {
  color: #374151;
}

.preview-display {
  flex: 1;
  padding: 1.5rem;
  background: white;
}

.preview-text {
  color: #374151;
  line-height: 1.6;
  font-size: 0.875rem;
  white-space: pre-wrap;
  position: relative;
}

.preview-content-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 0.5rem;
}

.edit-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: #6b7280;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  color: #374151;
  background: #f3f4f6;
}

.edit-btn svg {
  width: 16px;
  height: 16px;
}

.edit-mode {
  margin-top: 0.5rem;
}

.edit-textarea {
  width: 100%;
  min-height: 100px;
  padding: 0.75rem;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  font-size: 0.875rem;
  line-height: 1.6;
  color: #374151;
  resize: none;
  background: #f9fafb;
}

.edit-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  background: white;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  justify-content: flex-end;
}

.save-edit-btn,
.cancel-edit-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.save-edit-btn {
  background: #10b981;
  color: white;
  border: none;
}

.save-edit-btn:hover {
  background: #059669;
}

.cancel-edit-btn {
  background: white;
  color: #6b7280;
  border: 1px solid #e5e5e5;
}

.cancel-edit-btn:hover {
  background: #f9fafb;
  color: #4b5563;
}

.save-edit-btn svg,
.cancel-edit-btn svg {
  width: 14px;
  height: 14px;
}

.preview-image {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.image-details {
  margin-top: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.preview-section-item {
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  margin-bottom: 1rem;
  background: white;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e5e5;
}

.section-header h4 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.section-status {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  background: #e5e7eb;
  color: #6b7280;
}

.section-status.active {
  background: #dcfce7;
  color: #15803d;
}

.section-content {
  padding: 1rem;
}

.empty-state, .inactive-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.inactive-state {
  background: #f9fafb;
  border-radius: 0 0 8px 8px;
}

.preview-content {
  padding: 1rem;
  overflow-y: auto;
}

.preview-actions {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e5e5;
  background: white;
}

.preview-action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid #e5e5e5;
  background: white;
  color: #374151;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.preview-action-btn:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.preview-action-btn svg {
  width: 14px;
  height: 14px;
}

/* Share Dropdown */
.share-dropdown-container {
  position: relative;
  display: inline-block;
}

.share-btn {
  background-color: #4CAF50 !important;
  color: white !important;
  border: none !important;
}

.share-btn:hover:not(:disabled) {
  background-color: #45a049 !important;
}

.share-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background: white;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 180px;
  z-index: 1000;
}

.share-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  color: #374151;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.share-option:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.share-option:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.share-option svg {
  width: 18px;
  height: 18px;
}

/* Settings Button */
.settings-btn {
  background: none;
  border: 1px solid #e5e5e5;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 0.5rem;
  transition: all 0.2s ease;
}

.settings-btn:hover {
  background: #f5f5f5;
}

.settings-icon {
  width: 18px;
  height: 18px;
  color: #6b7280;
}

/* Settings Modal */
.settings-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.settings-modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.close-modal-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  color: #6b7280;
  border-radius: 6px;
}

.close-modal-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.close-modal-btn svg {
  width: 16px;
  height: 16px;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.form-section {
  margin-bottom: 1.5rem;
}

.form-section h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.required {
  color: #ef4444;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #374151;
  background: white;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e5e5;
  display: flex;
  justify-content: flex-end;
}

.save-btn {
  background: #10a37f;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.save-btn:hover {
  background: #0d8c6c;
}

/* Responsive */
@media (max-width: 1024px) {
  .preview-section {
    width: 30%;
  }
}

@media (max-width: 768px) {
  .generator-container {
    flex-direction: column;
  }
  
  .preview-section {
    width: 100%;
    height: 40%;
    border-left: none;
    border-top: 1px solid #e5e5e5;
  }
  
  .preview-section.hidden {
    height: 0;
    width: 100%;
  }
  
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
  
  .chat-header {
    padding: 1rem;
  }
  
  .message {
    padding: 0 1rem;
  }
  
  .settings-modal-content {
    width: 95%;
    max-height: 95vh;
  }
}
</style>