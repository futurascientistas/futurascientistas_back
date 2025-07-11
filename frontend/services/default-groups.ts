import axios from "axios";

const API_URL = "http://localhost:8000/usuarios/grupos/default/";

export type Group = {
  id: string;
  name: string;
};

export async function fetchGroups(): Promise<Group[]> {
  // const response = await axios.get(`${API_URL}`, {
  //   withCredentials: true,
  // });
  var data = [
    {
      id: 1,
      name: "admin",
    },
    {
      id: 2,
      name: "estudante",
    },
    {
      id: 3,
      name: "avaliadora",
    },
    {
      id: 4,
      name: "professora",
    },
  ];
  return data;
}
