import axios from "axios";

// Create an Axios instance
export const APIInstance = axios.create({
  baseURL: "http://127.0.0.1:5000", 
  headers: {
    "Content-Type": "application/json", 
  },
});

// Define the API methods
export const API = {
  question: async (params: { query: string }) => {
    try {
      const response = await APIInstance.post("/api/qa", params); 
      return response.data; 
    } catch (error) {
      console.error("Error while making API call:", error);
      throw error; 
    }
  },
};