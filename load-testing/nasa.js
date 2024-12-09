import http from 'k6/http';
import { sleep } from 'k6';
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';
import { SharedArray } from "k6/data";

// Load and parse NASA dataset
const requestsPerMinute = new SharedArray("requests", function() {
  const data = papaparse.parse(open('./NASA.csv'), { header: false }).data;
  // Remove header and empty last row
  data.shift();
  data.pop();
  // Extract request counts
  return data.map(row => parseInt(row[1]));
});

export const options = {
  duration: '45m'  // Duration to run the test
};

export default function() {
  const currentMinute = __ITER;
  const targetRequests = requestsPerMinute[currentMinute % requestsPerMinute.length];

  // Calculate delay between requests to achieve target rate
  // 60 seconds / requests_per_minute = seconds between requests
  const delayBetweenRequests = 60 / targetRequests;

  // Make request to IMDb API
  http.get('http://localhost:30080/api/actors/nm0000206');

  // Sleep for calculated delay
  sleep(delayBetweenRequests);
}
