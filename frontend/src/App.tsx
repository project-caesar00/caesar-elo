import { useState, useEffect } from 'react'
import { StackReview } from './components/StackReview'
import { ScrapeConfig } from './components/ScrapeConfig'
import { WebsiteList } from './components/WebsiteList'
import { SearchAggregation } from './components/SearchAggregation'
import './App.css'

type Page = 'review' | 'designvorlagen' | 'leads' | 'scrape' | 'aggregate'

function App() {
  const [page, setPage] = useState<Page>('aggregate')

  // Handle hash-based routing
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1) as Page
      if (['review', 'designvorlagen', 'leads', 'scrape', 'aggregate'].includes(hash)) {
        setPage(hash)
      } else {
        setPage('aggregate')
      }
    }

    handleHashChange() // Initial load
    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <h1>Caesar ELO</h1>
        <nav>
          <a href="#aggregate" className={page === 'aggregate' ? 'active' : ''}>Aggregieren</a>
          <a href="#review" className={page === 'review' ? 'active' : ''}>Review</a>
          <a href="#designvorlagen" className={page === 'designvorlagen' ? 'active' : ''}>Designvorlagen</a>
          <a href="#leads" className={page === 'leads' ? 'active' : ''}>Leads</a>
          <a href="#scrape" className={page === 'scrape' ? 'active' : ''}>Scrape</a>
        </nav>
      </header>
      <main>
        {page === 'aggregate' && <SearchAggregation />}
        {page === 'review' && <StackReview />}
        {page === 'designvorlagen' && <WebsiteList filter="designvorlage" title="Designvorlagen" />}
        {page === 'leads' && <WebsiteList filter="good_lead" title="Good Leads" />}
        {page === 'scrape' && <ScrapeConfig />}
      </main>
    </div>
  )
}

export default App

