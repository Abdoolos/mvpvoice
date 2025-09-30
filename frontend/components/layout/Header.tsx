'use client'

import { useState } from 'react'
import { 
  BellIcon,
  MagnifyingGlassIcon,
  SunIcon,
  MoonIcon,
  ComputerDesktopIcon,
  Bars3Icon
} from '@heroicons/react/24/outline'
import { useTheme } from '@/components/providers/ThemeProvider'
import { clsx } from 'clsx'

export function Header() {
  const { theme, setTheme, resolvedTheme } = useTheme()
  const [searchQuery, setSearchQuery] = useState('')

  const themeOptions = [
    { value: 'light', label: 'Lys', icon: SunIcon },
    { value: 'dark', label: 'Mørk', icon: MoonIcon },
    { value: 'system', label: 'System', icon: ComputerDesktopIcon },
  ]

  return (
    <header className="bg-white border-b border-gray-200 dark:bg-gray-800 dark:border-gray-700">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        
        {/* Left side - Mobile menu button and search */}
        <div className="flex items-center">
          {/* Mobile menu button */}
          <button
            type="button"
            className="md:hidden rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 dark:hover:bg-gray-700 dark:hover:text-gray-300"
          >
            <Bars3Icon className="h-6 w-6" />
          </button>

          {/* Search */}
          <div className="hidden sm:block ml-4">
            <div className="relative">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Søk i oppringinger..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full rounded-lg border-gray-300 bg-white pl-10 pr-3 py-2 text-sm placeholder-gray-500 focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-primary-400 dark:focus:ring-primary-400"
              />
            </div>
          </div>
        </div>

        {/* Right side - Notifications and theme switcher */}
        <div className="flex items-center space-x-4">
          
          {/* Theme switcher */}
          <div className="relative">
            <select
              value={theme}
              onChange={(e) => setTheme(e.target.value as any)}
              className="rounded-lg border-gray-300 bg-white text-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-primary-400 dark:focus:ring-primary-400"
            >
              {themeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Notifications */}
          <button
            type="button"
            className="relative rounded-full bg-white p-1 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:bg-gray-800 dark:hover:text-gray-300"
          >
            <BellIcon className="h-6 w-6" />
            {/* Notification badge */}
            <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white dark:ring-gray-800"></span>
          </button>

          {/* Status indicator */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center">
              <div className="h-2 w-2 rounded-full bg-green-400"></div>
              <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">
                System tilkoblet
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile search - only visible on small screens */}
      <div className="border-t border-gray-200 px-4 py-2 sm:hidden dark:border-gray-700">
        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Søk i oppringinger..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="block w-full rounded-lg border-gray-300 bg-white pl-10 pr-3 py-2 text-sm placeholder-gray-500 focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:focus:border-primary-400 dark:focus:ring-primary-400"
          />
        </div>
      </div>
    </header>
  )
}
