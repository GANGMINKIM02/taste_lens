const BASE=(process.env.NEXT_PUBLIC_API_BASE_URL || '/api').replace(/\/$/,'');

async function request<T>(path:string, init?:RequestInit):Promise<T>{
  const response=await fetch(`${BASE}${path}`,{
    ...init,
    headers:{'Content-Type':'application/json',...(init?.headers||{})},
  });
  if(!response.ok){
    let detail=`HTTP ${response.status}`;
    try{const body=await response.json(); detail=body?.detail||detail;}catch{}
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export const api=<T=any>(path:string)=>request<T>(path);
export const post=<T=any>(path:string,body?:unknown)=>request<T>(path,{method:'POST',body:body===undefined?undefined:JSON.stringify(body)});
export const patch=<T=any>(path:string,body?:unknown)=>request<T>(path,{method:'PATCH',body:body===undefined?undefined:JSON.stringify(body)});
