#include<stdio.h>
#include<string.h>
#include<stdlib.h>
#include<math.h>

int main(){
  char* a = "123\0";
  char* b = "23TR\'F\0";
  printf("%d\n", strlen(a));
  printf("%d\n", strlen(b));
  int c;
  for (c = 0; c < strlen(b); c ++)
    printf("%c\n", tolower(b[c]));
  int flag = 0;
  for (c = 0; c < strlen(b); c --)
    if (b[strlen(b) - c - 1] != a[strlen(a) - c - 1])
	  {flag = 1; break;}
  int i = 0;
  int j = 1;
  float f = 0.0;
  if (i == 1) printf("iiii\n");
  else printf("jjjjj\n");
  printf("%d\n", flag);
  unsigned long long next_random = 1;
  long long x;
  float *syn0;
  for (j = 0; j < 2; j ++){
  for (i = 0; i < 20; i ++)
  {
  x = posix_memalign((void **)&syn0, 128, (long long)200 * sizeof(float));
    next_random = next_random * (unsigned long long)25214903917 + 11;
    printf("%f ", ((next_random & 0xFFFF) / (float)65536) - 0.5); 	
  }
  printf("\n");
  }
  printf("\n\n");
  printf("%f\n", log(2.7));
  return 0;
}
