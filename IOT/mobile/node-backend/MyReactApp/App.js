import React, { useState } from 'react';
import { StyleSheet, View, Switch, Text } from 'react-native';
import { firebaseConfig } from './conf'; // Update this line


export default function App() {
  const { baseURL, apiKey } = firebaseConfig;

  // State for switches
  const [fretStates, setFretStates] = useState({
    0: false,
    1: false,
    2: false,
    3: false,
    4: false
  });
  const [isStrumming, setIsStrumming] = useState(false);

  const handleFretChange = async (fretNumber, value) => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      // Update local state
      setFretStates(prev => ({
        ...prev,
        [`fret_${fretNumber}`]: value
      }));

      // Send data to Firebase
      const data = {
        [`fret_${fretNumber}`]: value
      };

      const response = await fetch(`${baseURL}/frets.json?key=${apiKey}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      console.log('Firebase response:', await response.json());
    } catch (error) {
      console.error('Firebase request failed:', error);
    }
  };

  const handleStrumChange = async (value) => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      // Update local state
      setIsStrumming(value);

      // Send data to Firebase
      const data = {
        is_strumming: value
      };

      const response = await fetch(`${baseURL}/frets.json?key=${apiKey}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      console.log('Firebase response:', await response.json());
    } catch (error) {
      console.error('Firebase request failed:', error);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        Autonomous Music System Using Hand Gesture Recognition
      </Text>
      
      <View style={styles.contentContainer}>
        <View style={styles.fretContainer}>
          {[1, 2, 3, 4].map((fretNumber) => (
            <View key={fretNumber} style={styles.fretGroup}>
              <Text style={styles.fretLabel}>Fret {fretNumber}</Text>
              <Switch
                trackColor={{ false: "#767577", true: "#4CAF50" }}
                thumbColor={fretStates[`fret_${fretNumber}`] ? "#fff" : "#f4f3f4"}
                ios_backgroundColor="#3e3e3e"
                onValueChange={(value) => handleFretChange(fretNumber, value)}
                value={fretStates[`fret_${fretNumber}`]}
                style={styles.switch}
              />
            </View>
          ))}
        </View>

        <View style={styles.strumContainer}>
          <Text style={styles.strumLabel}>Strum Control</Text>
          <Switch
            trackColor={{ false: "#767577", true: "#2196F3" }}
            thumbColor={isStrumming ? "#fff" : "#f4f3f4"}
            ios_backgroundColor="#3e3e3e"
            onValueChange={handleStrumChange}
            value={isStrumming}
            style={styles.switch}
          />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000000',
    textAlign: 'center',
    marginBottom: 40,
    marginTop: 20,
  },
  contentContainer: {
    flex: 1,
    justifyContent: 'space-between',
  },
  fretContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  fretGroup: {
    width: '48%',
    backgroundColor: '#f5f5f5',
    padding: 20,
    borderRadius: 15,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    alignItems: 'center',
    elevation: 2,
  },
  fretLabel: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#000000',
    textAlign: 'center',
    marginBottom: 15,
  },
  strumContainer: {
    backgroundColor: '#f5f5f5',
    padding: 20,
    borderRadius: 15,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    marginTop: 20,
    alignItems: 'center',
    elevation: 2,
  },
  strumLabel: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#000000',
    textAlign: 'center',
    marginBottom: 15,
  },
  switch: {
    transform: [{ scaleX: 2.5 }, { scaleY: 2.5 }],
    marginVertical: 15,
  }
});