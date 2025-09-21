<template>
  <div class="home-container">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-text">✨ AI-Powered Content Localization</span>
        </div>
        <h1 class="hero-title">
          Transform Your Content for 
          <span class="gradient-text">Malaysia Markets</span>
        </h1>
        <p class="hero-description">
          Localize your content with AI precision. Adapt messaging, tone, and cultural nuances 
          for Malaysia market while maintaining your brand voice and authenticity.
        </p>
        
        <div class="hero-actions">
          <router-link to="/generator" class="btn-primary">
            <span>Start Generating</span>
            <svg viewBox="0 0 24 24" fill="none" class="btn-icon">
              <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2"/>
            </svg>
          </router-link>
        </div>
        
        <div class="hero-stats">
          <div class="stat">
            <div class="stat-number">10K+</div>
            <div class="stat-label">Content Pieces</div>
          </div>
          <div class="stat">
            <div class="stat-number">50+</div>
            <div class="stat-label">Languages</div>
          </div>
          <div class="stat">
            <div class="stat-number">100+</div>
            <div class="stat-label">Users</div>
          </div>
        </div>
      </div>
      
      <div class="hero-visual">
        <div class="visual-container">
          <div class="floating-card card-1">
            <div class="card-header">English → Malaysia Language</div>
            <div class="card-content">"Why didn’t you invite me?" → "Bojio"</div>
          </div>
          <div class="floating-card card-2">
            <div class="card-header">Tone Adaptation</div>
            <div class="card-content">Formal → Casual</div>
          </div>
          <div class="floating-card card-3">
            <div class="card-header">Cultural Context</div>
            <div class="card-content">"Potluck party" → "Makan-makan gathering"</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">Why Choose TransformLah?</h2>
          <p class="section-description">
            Powerful AI capabilities designed for modern content teams
          </p>
        </div>
        
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <h3 class="feature-title">Smart Localization</h3>
            <p class="feature-description">
              AI-powered translation that understands context, culture, and brand voice to deliver authentic localized content.
            </p>
          </div>
          
          
          <div class="feature-card">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21M13 7C13 9.20914 11.2091 11 9 11C6.79086 11 5 9.20914 5 7C5 4.79086 6.79086 3 9 3C11.2091 3 13 4.79086 13 7ZM23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89317 18.7122 8.75608 18.1676 9.45768C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <h3 class="feature-title">Analyze Insights</h3>
            <p class="feature-description">
              Understand your content better with built-in analytics that provide detailed insights into performance, engagement, and trends.
            </p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M3 15C3 15 5.5 17 9 17C12.5 17 15 15 15 15M9 11H9.01M15 11H15.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <h3 class="feature-title">Social Media Ready</h3>
            <p class="feature-description">
              Create platform-specific content that's optimized for engagement across different social media channels and audiences.
            </p>
          </div>

        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-content">
          <h2 class="cta-title">Ready to Go To Malaysia Market?</h2>
          <p class="cta-description">
            Join hundreds of companies using TransformLah to scale their global content strategy.
          </p>
          <div class="cta-actions">
            <router-link to="/generator" class="btn-primary">Start Free Trial</router-link>
            <button class="btn-outline">Schedule Demo</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'HomePage'
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #fafbfc 0%, #f8fafc 100%);
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Hero Section */
.hero-section {
  padding: 6rem 2rem 4rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  max-width: 1280px;
  margin: 0 auto;
}

.hero-content {
  text-align: left;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 2rem;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  letter-spacing: -0.02em;
}

.gradient-text {
  color: #667eea;
  font-weight: 800;
}

.hero-description {
  font-size: 1.25rem;
  color: #64748b;
  line-height: 1.7;
  margin-bottom: 3rem;
  max-width: 540px;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 4rem;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px rgba(102, 126, 234, 0.3);
  border: none;
  cursor: pointer;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  background: transparent;
  color: #64748b;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  color: #334155;
  background: rgba(0, 0, 0, 0.04);
}

.play-icon {
  width: 16px;
  height: 16px;
  color: #667eea;
}

.hero-stats {
  display: flex;
  gap: 3rem;
}

.stat {
  text-align: left;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

/* Hero Visual */
.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.visual-container {
  position: relative;
  width: 400px;
  height: 400px;
}

.floating-card {
  position: absolute;
  background: white;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
  animation: float 6s ease-in-out infinite;
}

.card-1 {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.card-2 {
  top: 40%;
  right: 10%;
  animation-delay: 2s;
}

.card-3 {
  bottom: 18%;
  left: 5%;
  animation-delay: 3s;
}

.card-header {
  font-size: 0.75rem;
  color: #667eea;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.card-content {
  font-size: 0.875rem;
  color: #334155;
  font-weight: 500;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  33% { transform: translateY(-20px) rotate(1deg); }
  66% { transform: translateY(-10px) rotate(-1deg); }
}

/* Features Section */
.features-section {
  padding: 6rem 0;
  background: white;
}

.section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.section-description {
  font-size: 1.125rem;
  color: #64748b;
  max-width: 600px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
  border-color: rgba(102, 126, 234, 0.2);
}

.feature-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 1.5rem;
}

.feature-icon svg {
  width: 24px;
  height: 24px;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 0.75rem;
}

.feature-description {
  color: #64748b;
  line-height: 1.6;
  font-size: 0.975rem;
}

/* CTA Section */
.cta-section {
  padding: 6rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.cta-content {
  text-align: center;
  color: white;
}

.cta-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.cta-description {
  font-size: 1.125rem;
  margin-bottom: 2rem;
  opacity: 0.9;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.cta-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
}

.btn-outline {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 1rem 2rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

/* Responsive */
@media (max-width: 768px) {
  .hero-section {
    grid-template-columns: 1fr;
    gap: 3rem;
    padding: 4rem 1rem 2rem;
    text-align: center;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .hero-stats {
    justify-content: center;
    gap: 2rem;
  }
  
  .visual-container {
    width: 300px;
    height: 300px;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .cta-title {
    font-size: 2rem;
  }
  
  .cta-actions {
    flex-direction: column;
  }
}
</style>