import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import FurniturePlacementTest from './pages/FurniturePlacementTest.jsx'
import Layout from './components/Layout.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<App />} />
          <Route path="furniture-placement" element={<FurniturePlacementTest />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
