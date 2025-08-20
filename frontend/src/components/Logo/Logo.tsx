import { Image } from '@mantine/core';
import logoSvg from '@/images/logo.svg';

export default function Logo() {
  return (
    <Image
      src={logoSvg}
      alt="Telefónica Tech - Local Government Hackathon - Somerset"
      width={50}
      height={50}
    />
  );
}
