<template>
  <div class="social-dashboard">
    <!-- Tab Navigation -->
    <div class="tab-navigation">
      <button 
        :class="{ active: activeTab === 'dashboard' }" 
        @click="activeTab = 'dashboard'"
        class="tab-button"
      >
        <i class="fas fa-chart-bar"></i>
        Dashboard
      </button>
      <button 
        :class="{ active: activeTab === 'insights' }" 
        @click="activeTab = 'insights'"
        class="tab-button"
      >
        <i class="fas fa-lightbulb"></i>
        Insights Analysis
      </button>
    </div>

    <!-- Dashboard Tab -->
    <div v-if="activeTab === 'dashboard'">
      <!-- Total Reach Summary -->
      <div class="reach-summary">
        <h2>Total Social Reach</h2>
        <div class="summary-stats-grid">
          <div class="stat-box total-followers">
            <span class="number">{{ formatNumber(socialSummary.total_followers) }}</span>
            <span class="label">Total Followers</span>
          </div>
          <div class="stat-box total-likes">
            <span class="number">{{ formatNumber(socialSummary.total_likes) }}</span>
            <span class="label">Total Likes</span>
          </div>
          <div class="stat-box total-views">
            <span class="number">{{ formatNumber(socialSummary.total_views) }}</span>
            <span class="label">Total Views</span>
          </div>
          <div class="stat-box platforms-connected">
            <span class="number">{{ socialSummary.platforms_connected }}/6</span>
            <span class="label">Platforms Connected</span>
          </div>
        </div>
      </div>

      <div class="connection-status">
        <!-- Facebook -->
        <div class="platform-card" :class="{ 'connected': facebookData.connected }">
          <div class="platform-header">
            <div class="platform-icon"><i class="fab fa-facebook"></i></div>
            <h3>Facebook</h3>
            <span class="status-badge" :class="{ 'connected': facebookData.connected }">
              {{ facebookData.connected ? 'Connected' : 'Not Connected' }}
            </span>
          </div>
          <a v-if="facebookData.profile_url" :href="facebookData.profile_url" target="_blank" class="profile-link">
            <i class="fas fa-external-link-alt"></i> View Page
          </a>
          <div v-if="facebookData.connected" class="platform-stats">
            <div class="stat-item"><span class="stat-label">Page Name</span><span class="stat-value">{{ facebookData.name || 'N/A' }}</span></div>
            <div class="stat-item"><span class="stat-label">Followers</span><span class="stat-value">{{ formatNumber(facebookData.followers) }}</span></div>
            <div class="stat-item"><span class="stat-label">Page Likes</span><span class="stat-value">{{ formatNumber(facebookData.likes) }}</span></div>
            <div class="stat-item"><span class="stat-label">Total Posts</span><span class="stat-value">{{ formatNumber(facebookData.posts) }}</span></div>
          </div>
        </div>

        <!-- Instagram -->
        <div class="platform-card" :class="{ 'connected': instagramData.connected }">
          <div class="platform-header">
            <div class="platform-icon"><i class="fab fa-instagram"></i></div>
            <h3>Instagram</h3>
            <span class="status-badge" :class="{ 'connected': instagramData.connected }">
              {{ instagramData.connected ? 'Connected' : 'Not Connected' }}
            </span>
          </div>
          <a v-if="instagramData.username" :href="'https://instagram.com/' + instagramData.username" target="_blank" class="profile-link">
            <i class="fas fa-external-link-alt"></i> View Profile
          </a>
          <div v-if="instagramData.connected" class="platform-stats">
            <div class="stat-item"><span class="stat-label">Username</span><span class="stat-value">{{ instagramData.username || 'N/A' }}</span></div>
            <div class="stat-item"><span class="stat-label">Followers</span><span class="stat-value">{{ formatNumber(instagramData.followers) }}</span></div>
            <div class="stat-item"><span class="stat-label">Following</span><span class="stat-value">{{ formatNumber(instagramData.following) }}</span></div>
            <div class="stat-item"><span class="stat-label">Total Posts</span><span class="stat-value">{{ formatNumber(instagramData.posts) }}</span></div>
          </div>
        </div>

        <!-- YouTube -->
        <div class="platform-card" :class="{ 'connected': youtubeData.connected }">
          <div class="platform-header">
            <div class="platform-icon"><i class="fab fa-youtube"></i></div>
            <h3>YouTube</h3>
            <span class="status-badge" :class="{ 'connected': youtubeData.connected }">
              {{ youtubeData.connected ? 'Connected' : 'Not Connected' }}
            </span>
          </div>
          <a v-if="youtubeData.channelUrl" :href="youtubeData.channelUrl" target="_blank" class="profile-link">
            <i class="fas fa-external-link-alt"></i> View Channel
          </a>
          <div v-if="youtubeData.connected" class="platform-stats">
            <div class="stat-item"><span class="stat-label">Channel Name</span><span class="stat-value">{{ youtubeData.channelName || 'N/A' }}</span></div>
            <div class="stat-item"><span class="stat-label">Subscribers</span><span class="stat-value">{{ formatNumber(youtubeData.subscribers) }}</span></div>
            <div class="stat-item"><span class="stat-label">Videos</span><span class="stat-value">{{ formatNumber(youtubeData.videos) }}</span></div>
            <div class="stat-item"><span class="stat-label">Total Views</span><span class="stat-value">{{ formatNumber(youtubeData.views) }}</span></div>
          </div>
        </div>

        <!-- TikTok -->
        <div class="platform-card" :class="{ 'connected': tiktokData.connected }">
          <div class="platform-header">
            <div class="platform-icon"><i class="fab fa-tiktok"></i></div>
            <h3>TikTok</h3>
            <span class="status-badge" :class="{ 'connected': tiktokData.connected }">
              {{ tiktokData.connected ? 'Connected' : 'Not Connected' }}
            </span>
          </div>
          <button v-if="!tiktokData.connected" @click="connectPlatform('tiktok')" class="connect-button">
            <i class="fas fa-plug"></i> Connect TikTok
          </button>
          <a v-if="tiktokData.profile_url" :href="tiktokData.profile_url" target="_blank" class="profile-link">
            <i class="fas fa-external-link-alt"></i> View Profile
          </a>
          <div v-if="tiktokData.connected" class="platform-stats">
            <div class="stat-item"><span class="stat-label">Username</span><span class="stat-value">{{ tiktokData.username || 'N/A' }}</span></div>
            <div class="stat-item"><span class="stat-label">Followers</span><span class="stat-value">{{ formatNumber(tiktokData.followers) }}</span></div>
            <div class="stat-item"><span class="stat-label">Following</span><span class="stat-value">{{ formatNumber(tiktokData.following) }}</span></div>
            <div class="stat-item"><span class="stat-label">Total Videos</span><span class="stat-value">{{ formatNumber(tiktokData.videos) }}</span></div>
          </div>
        </div>

        <!-- X (Twitter) -->
        <div class="platform-card" :class="{ 'connected': xData.connected }">
          <div class="platform-header">
            <div class="platform-icon"><i class="fab fa-x-twitter"></i></div>
            <h3>X (Twitter)</h3>
            <span class="status-badge" :class="{ 'connected': xData.connected }">
              {{ xData.connected ? 'Connected' : 'Not Connected' }}
            </span>
          </div>
          <button v-if="!xData.connected" @click="connectPlatform('x')" class="connect-button">
            <i class="fas fa-plug"></i> Connect X
          </button>
          <a v-if="xData.profile_url" :href="xData.profile_url" target="_blank" class="profile-link">
            <i class="fas fa-external-link-alt"></i> View Profile
          </a>
          <div v-if="xData.connected" class="platform-stats">
            <div class="stat-item"><span class="stat-label">Username</span><span class="stat-value">{{ xData.username || 'N/A' }}</span></div>
            <div class="stat-item"><span class="stat-label">Followers</span><span class="stat-value">{{ formatNumber(xData.followers) }}</span></div>
            <div class="stat-item"><span class="stat-label">Following</span><span class="stat-value">{{ formatNumber(xData.following) }}</span></div>
            <div class="stat-item"><span class="stat-label">Tweets</span><span class="stat-value">{{ formatNumber(xData.tweets) }}</span></div>
          </div>
        </div>

        <!-- LinkedIn -->
        <div class="platform-card" :class="{ 'connected': linkedinData.connected }">
          <div class="platform-header">
            <div class="platform-icon"><i class="fab fa-linkedin"></i></div>
            <h3>LinkedIn</h3>
            <span class="status-badge" :class="{ 'connected': linkedinData.connected }">
              {{ linkedinData.connected ? 'Connected' : 'Not Connected' }}
            </span>
          </div>
          <button v-if="!linkedinData.connected" @click="connectPlatform('linkedin')" class="connect-button">
            <i class="fas fa-plug"></i> Connect LinkedIn
          </button>
          <a v-if="linkedinData.profile_url" :href="linkedinData.profile_url" target="_blank" class="profile-link">
            <i class="fas fa-external-link-alt"></i> View Company Page
          </a>
          <div v-if="linkedinData.connected" class="platform-stats">
            <div class="stat-item"><span class="stat-label">Company Name</span><span class="stat-value">{{ linkedinData.companyName || 'N/A' }}</span></div>
            <div class="stat-item"><span class="stat-label">Followers</span><span class="stat-value">{{ formatNumber(linkedinData.followers) }}</span></div>
            <div class="stat-item"><span class="stat-label">Posts</span><span class="stat-value">{{ formatNumber(linkedinData.posts) }}</span></div>
            <div class="stat-item"><span class="stat-label">Employees</span><span class="stat-value">{{ formatNumber(linkedinData.employees) }}</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Insights Analysis Tab -->
    <div v-if="activeTab === 'insights'" class="insights-content">
      <div class="insights-summary">
        <h2>Content Insights</h2>
        <div class="summary-stats">
          <div class="summary-stat">
            <span class="number">{{ insightsData.summary.total_urls }}</span>
            <span class="label">Total Posts & Videos</span>
          </div>
          <div class="summary-stat">
            <span class="number">{{ insightsData.summary.platforms.length }}</span>
            <span class="label">Active Platforms</span>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="insights-main-content">
        <!-- Left Side: Content Sections -->
        <div class="insights-content-section">
          <!-- Instagram Section -->
          <div v-if="insightsData.instagram.length > 0" class="platform-content-section">
            <h3><i class="fab fa-instagram"></i> Instagram Posts</h3>
            <div class="content-list">
              <div v-for="(post, index) in insightsData.instagram" :key="'ig-'+index" class="content-item">
                <a :href="post.url" target="_blank" class="content-link">
                  <i class="fab fa-instagram"></i>
                  <span class="content-text">{{ post.caption || 'No caption' }}</span>
                  <i class="fas fa-external-link-alt"></i>
                </a>
              </div>
            </div>
          </div>

          <!-- YouTube Section -->
          <div v-if="insightsData.youtube.length > 0" class="platform-content-section">
            <h3><i class="fab fa-youtube"></i> YouTube Videos</h3>
            <div class="content-list">
              <div 
                v-for="(video, index) in insightsData.youtube" 
                :key="'yt-'+index" 
                class="content-item"
                :class="{ 'selected': selectedVideo && selectedVideo.video_id === video.video_id }"
                @click="selectVideo(video)"
              >
                <div class="content-link">
                  <i class="fab fa-youtube"></i>
                  <span class="content-text">{{ video.title || 'Untitled Video' }}</span>
                  <i class="fas fa-chevron-right"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Side: Conversation Box -->
        <div v-if="selectedVideo" class="conversation-section">
          <div class="conversation-header">
            <h3>Analyze Video: {{ selectedVideo.title }}</h3>
            <a :href="selectedVideo.url" target="_blank" class="video-link">
              <i class="fas fa-external-link-alt"></i> Open in YouTube
            </a>
          </div>

          <div class="conversation-messages" ref="messageContainer">
            <div v-for="(message, index) in conversation.messages" 
                :key="index" 
                class="message"
                :class="message.type">
              <div class="message-content">{{ message.content }}</div>
            </div>
          </div>

          <div class="conversation-input">
            <div v-if="conversation.error" class="error-message">
              {{ conversation.error }}
            </div>
            <div class="input-group">
              <textarea 
                v-model="conversation.prompt"
                placeholder="Ask about the video (e.g., 'What is the main topic?' or 'Analyze the engagement')"
                @keyup.enter.exact.prevent="sendPrompt"
                :disabled="conversation.loading"
              ></textarea>
              <button 
                @click="sendPrompt" 
                :disabled="!conversation.prompt.trim() || conversation.loading"
                class="send-button"
              >
                <i :class="conversation.loading ? 'fas fa-spinner fa-spin' : 'fas fa-paper-plane'"></i>
              </button>
            </div>
          </div>
        </div>

        <div v-else class="conversation-section no-selection">
          <div class="placeholder-content">
            <i class="fas fa-hand-pointer"></i>
            <p>Select a video or post to start analyzing</p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="insightsData.loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        Loading insights...
      </div>
    </div>
  </div>
</template>


<script>
const BACKEND_LOCAL_HOST_ENV = 'http://127.0.0.1:8000';

export default {
  name: 'SocialMediaPage',
  data() {
    return {
      activeTab: 'dashboard',
      socialSummary: {
        total_followers: 0,
        total_likes: 0,
        total_views: 0,
        platforms_connected: 0
      },
      insightsData: {
        loading: false,
        instagram: [],
        youtube: [],
        summary: {
          total_urls: 0,
          platforms: []
        }
      },
      selectedVideo: null,
      conversation: {
        loading: false,
        prompt: '',
        messages: [],
        error: null
      },
      youtubeData: {
        connected: false,
        channelName: '',
        subscribers: 0,
        videos: 0,
        views: 0,
        channelUrl: '',
        channelThumbnail: ''
      },
      linkedinData: {
        connected: false,
        companyName: '',
        followers: 0,
        posts: 0,
        employees: 0,
        profile_url: '',
        profile_picture: ''
      },
      xData: {
        connected: false,
        username: '',
        followers: 0,
        following: 0,
        tweets: 0,
        profile_url: '',
        profile_picture: ''
      },
      tiktokData: {
        connected: false,
        username: '',
        followers: 0,
        following: 0,
        videos: 0,
        likes: 0,
        profile_url: '',
        profile_picture: ''
      },
      facebookData: {
        connected: false,
        name: '',
        followers: 0,
        likes: 0,
        posts: 0,
        about: '',
        profile_url: '',
        profile_picture: ''
      },
      instagramData: {
        connected: false,
        username: '',
        followers: 0,
        following: 0,
        posts: 0,
        engagement_rate: 0,
        profile_picture: '',
        recent_posts: []
      }
    }
  },
  computed: {
    totalFollowers() {
      return this.socialSummary.total_followers;
    }
  },
  methods: {
    formatNumber(num) {
      if (!num) return '0';
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
      }
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
      }
      return num.toString();
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    getPlatformIcon(platform) {
      switch (platform) {
        case 'facebook':
          return 'fab fa-facebook';
        case 'instagram':
          return 'fab fa-instagram';
        case 'tiktok':
          return 'fab fa-tiktok';
        case 'youtube':
          return 'fab fa-youtube';
        default:
          return 'fas fa-share-alt';
      }
    },
    async connectPlatform(platform) {
      try {
        const response = await fetch(`${BACKEND_LOCAL_HOST_ENV}/social/connect/${platform}`, {
          method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
          await this.fetchSocialStats();
        }
      } catch (error) {
        console.error(`Error connecting to ${platform}:`, error);
      }
    },
    async fetchInsightsData() {
      this.insightsData.loading = true;
      try {
        const [urlsResponse, viewsResponse] = await Promise.all([
          fetch(`${BACKEND_LOCAL_HOST_ENV}/social/urls`),
          fetch(`${BACKEND_LOCAL_HOST_ENV}/social/views`)
        ]);
        
        const [urlsResult, viewsResult] = await Promise.all([
          urlsResponse.json(),
          viewsResponse.json()
        ]);
        
        if (urlsResult.success && urlsResult.data) {
          this.insightsData = {
            loading: false,
            instagram: urlsResult.data.instagram || [],
            youtube: urlsResult.data.youtube || [],
            summary: urlsResult.data.summary || {
              total_urls: 0,
              platforms: []
            }
          };
        }
        
        if (viewsResult && viewsResult.summary) {
          this.socialSummary = {
            total_followers: viewsResult.summary.total_followers || 0,
            total_likes: viewsResult.summary.total_likes || 0,
            total_views: viewsResult.summary.total_views || 0,
            platforms_connected: viewsResult.summary.platforms_connected || 0
          };
        }
      } catch (error) {
        console.error('Error fetching insights data:', error);
      } finally {
        this.insightsData.loading = false;
      }
    },

    selectVideo(video) {
      this.selectedVideo = video;
      this.conversation.messages = [];
      this.conversation.prompt = '';
      this.conversation.error = null;
    },

    async sendPrompt() {
      if (!this.conversation.prompt.trim() || !this.selectedVideo) return;

      this.conversation.loading = true;
      const prompt = this.conversation.prompt;

      this.conversation.messages.push({
        type: 'user',
        content: prompt
      });
      this.conversation.prompt = '';

      try {
        const response = await fetch(`${BACKEND_LOCAL_HOST_ENV}/social/youtube-analyze-llm`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            video_id: this.selectedVideo.video_id,
            prompt: prompt,
            max_comments: 50
          })
        });

        const result = await response.json();

        if (result.success) {
          this.conversation.messages.push({
            type: 'assistant',
            content: result.analysis || 'No analysis returned.'
          });
        } else {
          this.conversation.error = result.error || 'Failed to analyze video';
        }
      } catch (error) {
        console.error('Error analyzing video:', error);
        this.conversation.error = 'Error analyzing video';
      } finally {
        this.conversation.loading = false;
      }
    },
    async fetchSocialStats() {
      try {
        const [socialResponse, youtubeResponse, viewsResponse] = await Promise.all([
          fetch(`${BACKEND_LOCAL_HOST_ENV}/social/stats`),
          fetch(`${BACKEND_LOCAL_HOST_ENV}/social/get_youtube_channel`),
          fetch(`${BACKEND_LOCAL_HOST_ENV}/social/views`)
        ]);

        const [socialResult, youtubeResult, viewsResult] = await Promise.all([
          socialResponse.json(),
          youtubeResponse.json(),
          viewsResponse.json()
        ]);
        
        if (socialResult.success && socialResult.data) {
          const { facebook, instagram } = socialResult.data;
          
          if (facebook) {
            this.facebookData = {
              ...this.facebookData,
              ...facebook,
              connected: facebook.connected || false
            };
          }
          
          if (instagram) {
            this.instagramData = {
              ...this.instagramData,
              ...instagram,
              connected: instagram.connected || false
            };
          }
        }

        // Update social summary data
        if (viewsResult && viewsResult.summary) {
          this.socialSummary = {
            total_followers: viewsResult.summary.total_followers || 0,
            total_likes: viewsResult.summary.total_likes || 0,
            total_views: viewsResult.summary.total_views || 0,
            platforms_connected: viewsResult.summary.platforms_connected || 0
          };
        }

        if (youtubeResult.success && youtubeResult.channel) {
          const channel = youtubeResult.channel;
          this.youtubeData = {
            connected: true,
            channelName: channel.title,
            subscribers: parseInt(channel.subscribers),
            videos: parseInt(channel.total_videos),
            views: parseInt(channel.total_views),
            channelUrl: `https://youtube.com/channel/${channel.channel_id}`,
            channelThumbnail: channel.profile_picture
          };
        } else {
          this.youtubeData.connected = false;
        }
      } catch (error) {
        console.error('Error fetching social media stats:', error);
        this.facebookData.connected = false;
        this.instagramData.connected = false;
        this.youtubeData.connected = false;
      }
    }
  },
  watch: {
    activeTab(newTab) {
      if (newTab === 'insights') {
        this.fetchInsightsData();
      }
    }
  },
  mounted() {
    this.fetchSocialStats();
  }
}
</script>


<style scoped>
.social-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 2rem;
}

.dashboard-title {
  font-size: 2.5rem;
  color: #1e293b;
  margin-bottom: 2rem;
  text-align: center;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-fill-color: transparent;
}

.connection-status {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.platform-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.platform-card:hover {
  transform: translateY(-5px);
}

.platform-header {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.platform-header i {
  font-size: 1.5rem;
  margin-right: 1rem;
}

.platform-header h3 {
  margin: 0;
  font-size: 1.25rem;
  flex-grow: 1;
  color: #1e293b;
  font-weight: 600;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  background: #f1f5f9;
  color: #64748b;
  font-weight: 500;
}

.status-badge.connected {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.platform-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-top: 1.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.reach-summary {
  max-width: 1200px;
  margin: 0 auto 2.5rem;
  background: white;
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.reach-summary h2 {
  margin-bottom: 1.5rem;
  color: #1e293b;
  font-size: 1.5rem;
  font-weight: 600;
}

.summary-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin: 0 auto;
  max-width: 1000px;
}

.stat-box {
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.stat-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.number {
  display: block;
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.label {
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
}

.reach-summary {
  max-width: 1200px;
  margin: 0 auto 2.5rem;
  background: white;
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

/* Platform icon styles */
.platform-header .platform-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  margin-right: 15px;
}

.platform-header .fab {
  font-size: 24px;
}

.platform-card .fa-facebook {
  background: linear-gradient(135deg, #1877f2 0%, #0d5dc4 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.75rem;
}

.platform-card .fa-instagram {
  background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.75rem;
}

.platform-card .fa-tiktok {
  background: linear-gradient(135deg, #00f2ea 0%, #ff0050 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.75rem;
}

.platform-card .fa-youtube {
  background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.75rem;
}

.platform-card .fa-linkedin {
  background: linear-gradient(135deg, #0077b5 0%, #00a0dc 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.75rem;
}

.platform-card .fa-x-twitter {
  background: linear-gradient(135deg, #14171A 0%, #657786 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.75rem;
}

.connect-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem;
  margin: 1rem 0;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.connect-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.connect-button i {
  font-size: 1rem;
}

/* Profile link styles */
.profile-link {
  display: inline-flex;
  align-items: center;
  color: #1e293b;
  text-decoration: none;
  margin-top: 15px;
  padding: 8px 16px;
  background: #f8fafc;
  border-radius: 20px;
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
}

.profile-link:hover {
  background: #f1f5f9;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.profile-link i {
  margin-right: 8px;
  font-size: 14px;
}

/* Hover effects */
.platform-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 35px rgba(0, 0, 0, 0.12);
}

/* Tab Navigation */
.tab-navigation {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 0 1rem;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  border: none;
  background: white;
  border-radius: 8px;
  color: #64748b;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.tab-button i {
  font-size: 1.1rem;
}

.tab-button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.tab-button:hover:not(.active) {
  background: #f1f5f9;
  transform: translateY(-1px);
}

/* Insights Analysis Styles */
.insights-content {
  max-width: 1200px;
  margin: 0 auto;
}

.insights-summary {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  text-align: center;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.insights-summary h2 {
  margin-bottom: 1.5rem;
  color: #1e293b;
  font-size: 1.5rem;
  font-weight: 600;
}

.summary-stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
}

.summary-stat {
  background: #f8fafc;
  border-radius: 12px;
  padding: 1.5rem;
  min-width: 200px;
  border: 1px solid #e2e8f0;
}

.insights-main-content {
  display: grid;
  grid-template-columns: minmax(300px, 1fr) minmax(400px, 1fr);
  gap: 2rem;
  margin-bottom: 2rem;
}

.insights-content-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.platform-content-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.platform-content-section h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  color: #1e293b;
  font-size: 1.25rem;
  font-weight: 600;
}

.content-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.content-item {
  background: #f8fafc;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.content-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  color: #1e293b;
  text-decoration: none;
  transition: all 0.2s ease;
}

.content-link:hover {
  background: #f1f5f9;
  transform: translateX(5px);
}

.content-text {
  flex-grow: 1;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  color: #64748b;
  font-size: 1.1rem;
}

.fa-spinner {
  color: #667eea;
}

/* Conversation Styles */
.conversation-section {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 50px);
  position: sticky;
  top: 2rem;
  color: black;
}

.conversation-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 1.25rem;
  font-weight: 600;
}

.video-link {
  color: #667eea;
  text-decoration: none;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.conversation-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  max-width: 85%;
  padding: 1rem;
  border-radius: 12px;
  font-size: 0.925rem;
  line-height: 1.5;
}

.message.user {
  background: #f8fafc;
  margin-left: auto;
  border: 1px solid #e2e8f0;
}

.message.assistant {
  background: #eef2ff;
  margin-right: auto;
  border: 1px solid #c7d2fe;
}

.conversation-input {
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.input-group {
  display: flex;
  gap: 1rem;
}

.input-group textarea {
  flex-grow: 1;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem;
  resize: none;
  height: 45px;
  font-size: 0.925rem;
  line-height: 1.5;
  transition: all 0.2s ease;
}

.input-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.send-button {
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.send-button:hover:not(:disabled) {
  background: #5a67d8;
  transform: translateY(-1px);
}

.send-button:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.no-selection {
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-content {
  text-align: center;
  color: #64748b;
}

.placeholder-content i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.placeholder-content p {
  font-size: 1.1rem;
  margin: 0;
}

.content-item {
  cursor: pointer;
  transition: all 0.2s ease;
}

.content-item:hover {
  background: #f8fafc;
  transform: translateX(5px);
}

.content-item.selected {
  background: #eef2ff;
  border-color: #c7d2fe;
}

.content-item.selected .content-link {
  color: #667eea;
}

.message-content {
  white-space: pre-wrap;  /* keeps line breaks */
  line-height: 1.6;
  font-size: 15px;
}

.message-content h3 {
  font-size: 18px;
  margin: 10px 0;
  font-weight: 600;
}

.message-content ul {
  margin-left: 20px;
  list-style: disc;
}
</style>