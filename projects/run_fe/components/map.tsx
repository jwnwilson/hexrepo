import React, { useRef, useEffect } from 'react';
import * as maptilersdk from '@maptiler/sdk';
import "@maptiler/sdk/dist/maptiler-sdk.css";
import './map.css';

export default function Map() {
  const mapContainer = useRef(null);
  const map = useRef<maptilersdk.Map | null>(null);
  maptilersdk.config.apiKey = process.env.EXPO_PUBLIC_MAPTILER_API_KEY || '';
  const tokyo = { lng: 139.753, lat: 35.6844 };
  const zoom = 14;

  useEffect(() => {
    if (mapContainer.current) {
      map.current = new maptilersdk.Map({
        container: mapContainer.current,
        style: maptilersdk.MapStyle.OUTDOOR,
        center: [tokyo.lng, tokyo.lat],
        zoom: zoom,
        terrain: true,
        terrainControl: true,
        pitch: 30,
        bearing: -100.86,
        maxPitch: 50,
      });
    }
  }, [tokyo, zoom]);

  return (
    <div className="map-wrap">
      <div ref={mapContainer} className="map" />
    </div>
  );
}
