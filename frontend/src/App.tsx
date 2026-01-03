import { StackReview } from './components/StackReview'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Caesar ELO</h1>
        <nav>
          <a href="#review" className="active">Review</a>
          <a href="#designvorlagen">Designvorlagen</a>
          <a href="#leads">Leads</a>
          <a href="#scrape">Scrape</a>
        </nav>
      </header>
      <main>
        <StackReview />
      </main>
    </div>
  )
}

export default App
