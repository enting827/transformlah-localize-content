<template>
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <div class="brand-logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="brand-name">TransformLah</span>
        </div>
      </div>
      <div class="nav-center">
        <div class="nav-links">
          <router-link to="/" class="nav-link" exact-active-class="active">
            <span class="link-text">Home</span>
          </router-link>
          <router-link to="/generator" class="nav-link" active-class="active">
            <span class="link-text">Generator</span>
          </router-link>
          <router-link to="/social-media" class="nav-link" active-class="active">
            <span class="link-text">Social Media</span>
          </router-link>
        </div>
      </div>
      <div class="nav-actions">
        <button class="btn-secondary">Sign In</button>
        <button class="btn-primary">Get Started</button>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavigationBar'
}
</script>

<style scoped>
.navbar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 0;
}

.nav-container {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  height: 80px;
}

.nav-brand {
  display: flex;
  align-items: center;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.logo-icon svg {
  width: 20px;
  height: 20px;
}

.brand-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
  letter-spacing: -0.02em;
}

.nav-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(0, 0, 0, 0.04);
  padding: 4px;
  border-radius: 12px;
}

.nav-link {
  color: #64748b;
  text-decoration: none;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  position: relative;
}

.link-text {
  position: relative;
  z-index: 1;
}

.nav-link:hover {
  color: #334155;
  background: rgba(255, 255, 255, 0.8);
}

.nav-link.active {
  color: #1e293b;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-secondary {
  background: transparent;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #64748b;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: rgba(0, 0, 0, 0.04);
  border-color: rgba(0, 0, 0, 0.2);
  color: #334155;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

@media (max-width: 768px) {
  .nav-container {
    padding: 1rem;
    height: auto;
    flex-wrap: wrap;
    gap: 1rem;
  }
  
  .nav-center {
    order: 3;
    flex-basis: 100%;
    justify-content: center;
  }
  
  .nav-actions {
    gap: 0.5rem;
  }
  
  .btn-secondary,
  .btn-primary {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
  
  .brand-name {
    font-size: 1.25rem;
  }
}

@media (max-width: 480px) {
  .nav-links {
    gap: 0.25rem;
    padding: 2px;
  }
  
  .nav-link {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }
}
</style>