import axios from 'axios';

const secFillingsApi = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000,
});

export interface GetSecFillingsParams {
  ticker: string;
  reportType: string;
  afterDate: string;
  beforeDate: string;
  includeAmends: boolean;
  limit?: number;
  downloadDetails?: boolean;
}

export async function getSecFillings(params: GetSecFillingsParams) {
  try {
    const response = await secFillingsApi.get('/fetch-sec-filings/', {
      params: {
        ticker: params.ticker,
        report_type: params.reportType,
        after_date: params.afterDate,
        before_date: params.beforeDate,
        include_amends: params.includeAmends,
        limit: params.limit,
        download_details: params.downloadDetails,
      }
    });
    return response.data; 
  } catch (error) {
    console.error('Error while fetching SEC fillings data:', error);
    return null;
  }
}