'use client'

import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
  resolvedTheme: 'light' | 'dark'
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('system')
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    const stored = localStorage.getItem('theme') as Theme
    if (stored) {
      setTheme(stored)
    }
  }, [])

  useEffect(() => {
    const root = window.document.documentElement
    
    const updateTheme = () => {
      let resolved: 'light' | 'dark'
      
      if (theme === 'system') {
        resolved = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      } else {
        resolved = theme
      }
      
      setResolvedTheme(resolved)
      
      root.classList.remove('light', 'dark')
      root.classList.add(resolved)
      
      // Update CSS variables for toast
      if (resolved === 'dark') {
        root.style.setProperty('--toast-bg', '#374151')
        root.style.setProperty('--toast-color', '#f9fafb')
        root.style.setProperty('--toast-border', '#4b5563')
      } else {
        root.style.setProperty('--toast-bg', '#ffffff')
        root.style.setProperty('--toast-color', '#111827')
        root.style.setProperty('--toast-border', '#e5e7eb')
      }
    }
    
    updateTheme()
    localStorage.setItem('theme', theme)
    
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    if (theme === 'system') {
      mediaQuery.addEventListener('change', updateTheme)
      return () => mediaQuery.removeEventListener('change', updateTheme)
    }
  }, [theme])

  const value = {
    theme,
    setTheme,
    resolvedTheme,
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}
