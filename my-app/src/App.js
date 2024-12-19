import React from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import LoginPage from './Login'
import DoctorTitle from './DoctorTitle'
import DoctorSignup from './DoctorSignup'
import Userpage from './UserPage'
import Admin from './Admin'

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<LoginPage/>} />
        <Route path='/doctortitle' element={<DoctorTitle/>} />
        <Route path='/userpage' element={<Userpage/>} />
        <Route path='/doctorsignup' element={<DoctorSignup/>} />
        <Route path='/Admin' element={<Admin/>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
