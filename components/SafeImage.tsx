'use client';
import Image from 'next/image';
import {CSSProperties,useState} from 'react';

type Props={src?:string|null;alt:string;kind?:'food'|'restaurant'|'menu';className?:string;style?:CSSProperties;priority?:boolean};
const fallbacks={food:'/fallback/food.webp',restaurant:'/fallback/restaurant.webp',menu:'/fallback/menu.webp'};
export default function SafeImage({src,alt,kind='food',className,style,priority=false}:Props){
 const [current,setCurrent]=useState(src||fallbacks[kind]);
 return <Image src={current} alt={alt} width={kind==='restaurant'?1200:800} height={kind==='restaurant'?800:600} className={className} style={{objectFit:'cover',...style}} priority={priority} onError={()=>setCurrent(fallbacks[kind])}/>;
}
