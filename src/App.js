// src/App.js
import React, { useState } from 'react';
import MapComponent from './MapComponent';
import SearchBar from './SearchBar';
import './App.css';

function App() {
  const [query, setQuery] = useState('');

  const handleSearch = (query) => {
    setQuery(query);
  };

  return (
    <div className="App">
      <SearchBar onSearch={handleSearch} />
      <MapComponent query={query} />
    </div>
  );
}

export default App;
