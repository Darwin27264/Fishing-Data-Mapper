// src/MapComponent.js
import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const MapComponent = ({ query }) => {
  const [lakes, setLakes] = useState([]);
  const [filteredLakes, setFilteredLakes] = useState([]);

  useEffect(() => {
    fetch('/lakes.json')
      .then(response => response.json())
      .then(data => {
        setLakes(data);
        setFilteredLakes(data);
      });
  }, []);

  useEffect(() => {
    if (query) {
      const lowerCaseQuery = query.toLowerCase();
      const filtered = lakes.filter(lake =>
        lake.name.toLowerCase().includes(lowerCaseQuery) ||
        lake.species.some(fish => fish.toLowerCase().includes(lowerCaseQuery))
      );
      setFilteredLakes(filtered);
    } else {
      setFilteredLakes(lakes);
    }
  }, [query, lakes]);

  return (
    <MapContainer center={[39.0968, -120.0324]} zoom={5} style={{ height: "100vh", width: "100%" }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
      />
      {filteredLakes.map(lake => (
        <Marker key={lake.id} position={lake.location}>
          <Popup>
            <h2>{lake.name}</h2>
            <ul>
              {lake.species.map((fish, index) => (
                <li key={index}>{fish}</li>
              ))}
            </ul>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default MapComponent;
