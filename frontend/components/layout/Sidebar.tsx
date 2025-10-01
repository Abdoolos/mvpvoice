'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  HomeIcon,
  PhoneIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CloudArrowUpIcon,
  Cog6ToothIcon,
  UserCircleIcon
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Oppringinger', href: '/oppringinger', icon: PhoneIcon },
  { name: 'Last opp', href: '/last-opp', icon: CloudArrowUpIcon },
  { name: 'Rapporter', href: '/rapporter', icon: ChartBarIcon },
  { name: 'Dokumenter', href: '/dokumenter', icon: DocumentTextIcon },
  { name: 'Innstillinger', href: '/innstillinger', icon: Cog6ToothIcon },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="sidebar">
      {/* Logo/Header */}
      <div className="sidebar-header">
        <div className="flex items-center">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600">
            <PhoneIcon className="h-5 w-5 text-white" />
          </div>
          <div className="ml-3">
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
              AI Callcenter
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              AI Assistant
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <ul className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={clsx(
                    'nav-link',
                    isActive ? 'nav-link-active' : 'nav-link-inactive'
                  )}
                >
                  <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                  {item.name}
                </Link>
              </li>
            )
          })}
        </ul>

        {/* Secondary navigation */}
        <div className="mt-8">
          <h3 className="px-3 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
            System
          </h3>
          <ul className="mt-2 space-y-1">
            <li>
              <Link
                href="/profil"
                className="nav-link nav-link-inactive"
              >
                <UserCircleIcon className="mr-3 h-5 w-5 flex-shrink-0" />
                Profil
              </Link>
            </li>
          </ul>
        </div>
      </nav>

      {/* Footer */}
      <div className="flex-shrink-0 p-4">
        <div className="rounded-lg bg-primary-50 p-3 dark:bg-primary-900/20">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <img 
                src="/avatars/myimage1.png" 
                alt="User Avatar" 
                className="h-8 w-8 rounded-full object-cover"
                onError={(e) => {
                  // Fallback to initials if image fails to load
                  e.currentTarget.style.display = 'none';
                  const nextElement = e.currentTarget.nextElementSibling as HTMLElement;
                  if (nextElement) {
                    nextElement.style.display = 'flex';
                  }
                }}
              />
              <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center" style={{display: 'none'}}>
                <span className="text-sm font-medium text-white">AA</span>
              </div>
            </div>
            <div className="ml-3 min-w-0 flex-1">
              <p className="text-sm font-medium text-primary-700 dark:text-primary-300">
                Admin User
              </p>
              <p className="text-xs text-primary-500 dark:text-primary-400">
                Designer & Developer
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
