import { Image } from '@mantine/core';
import logoSvg from '@/images/logo.svg';

export default function Logo() {
  return (
    <Image
      src={logoSvg}
      alt="Microsoft and Telefónica Tech - Local Government Hackathon"
      width={50}
      height={50}
    />
  );
}
