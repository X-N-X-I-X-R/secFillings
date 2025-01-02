import React, { useState } from 'react';
import { StyleSheet, View, Text, Button, TextInput, TouchableOpacity, ScrollView } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { getSecFillings } from '../api/secFillingsApi';

export default function App() {
  const [ticker, setTicker] = useState('');
  const [reportType, setReportType] = useState('10-K');
  const [year, setYear] = useState('2024');
  const [quarter, setQuarter] = useState('Q1');
  const [includeAmends, setIncludeAmends] = useState(false);
  const [limit, setLimit] = useState('');
  const [downloadDetails, setDownloadDetails] = useState(true);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleToggleAmends = () => {
    setIncludeAmends(!includeAmends);
  };

  const handleToggleDownloadDetails = () => {
    setDownloadDetails(!downloadDetails);
  };

  const handleSubmit = async () => {
    setLoading(true);

    // Define the date range based on the user's input
    let afterDate, beforeDate;
    if (reportType === '10-Q') {
      // Calculate quarter dates
      const quarterDates = {
        Q1: [`${year}-01-01`, `${year}-03-31`],
        Q2: [`${year}-04-01`, `${year}-06-30`],
        Q3: [`${year}-07-01`, `${year}-09-30`],
        Q4: [`${year}-10-01`, `${year}-12-31`],
      };
      [afterDate, beforeDate] = quarterDates[quarter as keyof typeof quarterDates];
    } else {
      afterDate = `${year}-01-01`;
      beforeDate = `${year}-12-31`;
    }

    const data = await getSecFillings({
      ticker,
      reportType,
      afterDate,
      beforeDate,
      includeAmends,
      limit: limit ? parseInt(limit) : undefined,
      downloadDetails,
    });

    setResponse(data);
    setLoading(false);
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>SEC Filings Search</Text>

      <Text style={styles.label}>Ticker</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter Ticker (e.g., AAPL)"
        value={ticker}
        onChangeText={setTicker}
      />

      <Text style={styles.label}>Form Type</Text>
      <Picker
        selectedValue={reportType}
        onValueChange={(value) => setReportType(value)}
        style={styles.picker}
      >
        <Picker.Item label="10-K" value="10-K" />
        <Picker.Item label="10-Q" value="10-Q" />
        <Picker.Item label="8-K" value="8-K" />
        <Picker.Item label="13F-NT" value="13F-NT" />
        <Picker.Item label="13F-HR" value="13F-HR" />
        <Picker.Item label="SC 13G" value="SC 13G" />
        <Picker.Item label="SD" value="SD" />
      </Picker>

      {reportType === '10-Q' && (
        <>
          <Text style={styles.label}>Quarter</Text>
          <Picker
            selectedValue={quarter}
            onValueChange={(value) => setQuarter(value)}
            style={styles.picker}
          >
            <Picker.Item label="Q1" value="Q1" />
            <Picker.Item label="Q2" value="Q2" />
            <Picker.Item label="Q3" value="Q3" />
            <Picker.Item label="Q4" value="Q4" />
          </Picker>
        </>
      )}

      <Text style={styles.label}>Year</Text>
      <Picker
        selectedValue={year}
        onValueChange={(value) => setYear(value)}
        style={styles.picker}
      >
        {Array.from({ length: 10 }, (_, i) => (
          <Picker.Item key={i} label={`${2024 - i}`} value={`${2024 - i}`} />
        ))}
      </Picker>

      <Text style={styles.label}>Include Amendments?</Text>
      <TouchableOpacity style={styles.toggleButton} onPress={handleToggleAmends}>
        <Text style={styles.toggleText}>
          {includeAmends ? 'Yes (Click to Disable)' : 'No (Click to Enable)'}
        </Text>
      </TouchableOpacity>

      <Text style={styles.label}>Limit</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter Limit (optional)"
        value={limit}
        onChangeText={setLimit}
        keyboardType="numeric"
      />

      <Text style={styles.label}>Download Details?</Text>
      <TouchableOpacity style={styles.toggleButton} onPress={handleToggleDownloadDetails}>
        <Text style={styles.toggleText}>
          {downloadDetails ? 'Yes (Click to Disable)' : 'No (Click to Enable)'}
        </Text>
      </TouchableOpacity>

      <Button
        title={loading ? 'Fetching...' : 'Fetch Filings'}
        onPress={handleSubmit}
        disabled={loading}
      />

      {response && (
        <View style={styles.responseContainer}>
          <Text style={styles.responseTitle}>Response:</Text>
          <Text style={styles.responseText}>{JSON.stringify(response, null, 2)}</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 15,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    padding: 10,
    marginTop: 10,
    backgroundColor: '#fff',
  },
  picker: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    backgroundColor: '#fff',
    marginTop: 10,
  },
  toggleButton: {
    marginTop: 10,
    padding: 10,
    backgroundColor: '#007BFF',
    borderRadius: 5,
  },
  toggleText: {
    color: '#fff',
    textAlign: 'center',
    fontSize: 16,
  },
  responseContainer: {
    marginTop: 20,
    padding: 10,
    backgroundColor: '#fff',
    borderRadius: 5,
  },
  responseTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  responseText: {
    fontSize: 14,
    color: '#333',
    marginTop: 10,
  },
});