import React, { useState, useEffect } from 'react'
import { Zap, Bell, User, Search, Moon, Sun } from 'lucide-react'
import './Header.css'

const Header = () => {
  const [isDark, setIsDark] = useState(() => {
    return document.body.classList.contains('dark') ||
      localStorage.getItem('theme') === 'dark' ||
      (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)
  })

  useEffect(() => {
    if (isDark) {
      document.body.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.body.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [isDark])

  return (
    <header className="top-header">
      <div className="header-left">
        <Zap size={16} fill="currentColor" color="#0d99ff" />
        <h1 className="header-title">Precision Agriculture Platform</h1>
      </div>

      <div className="header-center">
        <div className="search-bar">
          <Search size={14} />
          <input type="text" placeholder="Search coordinates..." />
        </div>
      </div>

      <div className="header-right">
        <button
          className="header-action-btn theme-toggle"
          onClick={() => setIsDark(!isDark)}
          title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {isDark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button className="header-action-btn"><Bell size={18} /></button>
        <div className="user-profile">
          <div className="avatar">JD</div>
          <span className="user-name">John Doe</span>
        </div>
      </div>
    </header>
  )
}

export default Header
