import http from 'k6/http';
import { sleep } from 'k6';
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';
import { SharedArray } from "k6/data";

// EDIT this to change how many rows to simulate
const DURATION = '10s' // how many rows of the CSV file you want to simulate, where each row takes 1 second

// import and parse the NASA data csv file
const load = [];
const csvData = new SharedArray("csvData", function() {
  return papaparse.parse(open('./NASA.csv'), { header: false }).data;
});
// add request count for each timestamp
for (var i = 0; i < csvData.length; i++) {
  load.push(csvData[i][1]);
  if (Number.isNaN(csvData[i][1]) ) {
    console.error(csvData[i][1], "NaN");
  }

}
// remove first row (which contains the CSV header)
load.shift();

// remove last entry as CSV files may contain an empty row
load.pop();

// spin up a number of Virtual Users equal to our maximum load (make this much smaller in local testing to save compute :> )
const MAX_USERS = Math.max(...load);

// which row of the csv file we are currently simulating (starts at 0)
var row = 0;

export const options = {
  // A number specifying the number of VUs to run concurrently.
  vus: MAX_USERS,
  // A string specifying the total duration of the test run.
  duration: DURATION,

  // The following section contains configuration options for execution of this
  // test script in Grafana Cloud.
  //
  // See https://grafana.com/docs/grafana-cloud/k6/get-started/run-cloud-tests-from-the-cli/
  // to learn about authoring and running k6 test scripts in Grafana k6 Cloud.
  //
  // cloud: {
  //   // The ID of the project to which the test is assigned in the k6 Cloud UI.
  //   // By default tests are executed in default project.
  //   projectID: "",
  //   // The name of the test in the k6 Cloud UI.
  //   // Test runs with the same name will be grouped.
  //   name: "nasa.js"
  // },

  // Uncomment this section to enable the use of Browser API in your tests.
  //
  // See https://grafana.com/docs/k6/latest/using-k6-browser/running-browser-tests/ to learn more
  // about using Browser API in your test scripts.
  //
  // scenarios: {
  //   // The scenario name appears in the result summary, tags, and so on.
  //   // You can give the scenario any name, as long as each name in the script is unique.
  //   ui: {
  //     // Executor is a mandatory parameter for browser-based tests.
  //     // Shared iterations in this case tells k6 to reuse VUs to execute iterations.
  //     //
  //     // See https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/ for other executor types.
  //     executor: 'shared-iterations',
  //     options: {
  //       browser: {
  //         // This is a mandatory parameter that instructs k6 to launch and
  //         // connect to a chromium-based browser, and use it to run UI-based
  //         // tests.
  //         type: 'chromium',
  //       },
  //     },
  //   },
  // }
};

// The function that defines VU logic.
//
// See https://grafana.com/docs/k6/latest/examples/get-started-with-k6/ to learn more
// about authoring k6 scripts.
//
export default function() {
  // flip a coin, sending a request on heads.
  // in expectation, this creates the required number of requests per row in the CSV file
  const randomValue = Math.random();

  // right now, we are simulating one row with 1 second. If you want to simulate one row with 1 minute, simply divide this by 60
  if (randomValue < load[row] / parseFloat(MAX_USERS)) {
    http.get('http://localhost:30080/api/actors/nm0000206'); // simulates a random GET request (this doesn't really matter, we care about performance instead)
  }

  // this Virtual User will move on to the next row / timestamp
  row += 1;
  sleep(1);
}
