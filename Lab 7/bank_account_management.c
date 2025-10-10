#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ACCOUNTS 50
#define NAME_LEN 50
#define ADDRESS_LEN 100
#define PHONE_LEN 15
#define EMAIL_LEN 50

typedef struct {
    int acc_no;
    char name[NAME_LEN];
    char address[ADDRESS_LEN];
    char phone[PHONE_LEN];
    char email[EMAIL_LEN];
    char type[10]; // Savings/Current
    double balance;
} Account;

int main() {
    Account accounts[MAX_ACCOUNTS];
    int count = 0;
    int choice = -1;

    while (choice != 0) {
        printf("\n=== BANK MANAGEMENT SYSTEM ===\n");
        printf("1. Add New Account\n");
        printf("2. Delete Account\n");
        printf("3. Deposit\n");
        printf("4. Withdraw\n");
        printf("5. Transfer\n");
        printf("6. Display Account\n");
        printf("7. Display All Accounts\n");
        printf("8. Apply Interest\n");
        printf("9. Monthly Statement\n");
        printf("0. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        int acc_no, i, j;
        double amount;
        char temp[100];

        switch(choice) {
            case 1:
                if(count >= MAX_ACCOUNTS) {
                    printf("Maximum accounts reached!\n");
                    break;
                }
                accounts[count].acc_no = count + 1;
                printf("Enter Name: ");
                scanf(" %[^\n]", accounts[count].name);
                printf("Enter Address: ");
                scanf(" %[^\n]", accounts[count].address);
                printf("Enter Phone: ");
                scanf(" %[^\n]", accounts[count].phone);
                printf("Enter Email: ");
                scanf(" %[^\n]", accounts[count].email);
                printf("Enter Account Type (Savings/Current): ");
                scanf("%s", accounts[count].type);
                accounts[count].balance = 0.0;
                printf("Account created! Account Number: %d\n", accounts[count].acc_no);
                count++;
                break;

            case 2:
                printf("Enter Account Number to delete: ");
                scanf("%d", &acc_no);
                for(i=0; i<count; i++) {
                    if(accounts[i].acc_no == acc_no) {
                        for(j=i; j<count-1; j++) {
                            accounts[j] = accounts[j+1];
                        }
                        count--;
                        printf("Account %d deleted.\n", acc_no);
                        break;
                    }
                }
                if(i==count) printf("Account not found!\n");
                break;

            case 3:
                printf("Enter Account Number to deposit: ");
                scanf("%d", &acc_no);
                printf("Enter Amount: ");
                scanf("%lf", &amount);
                for(i=0; i<count; i++) {
                    if(accounts[i].acc_no == acc_no) {
                        accounts[i].balance += amount;
                        printf("Deposited %.2lf. New Balance: %.2lf\n", amount, accounts[i].balance);
                        break;
                    }
                }
                if(i==count) printf("Account not found!\n");
                break;

            case 4:
                printf("Enter Account Number to withdraw: ");
                scanf("%d", &acc_no);
                printf("Enter Amount: ");
                scanf("%lf", &amount);
                for(i=0; i<count; i++) {
                    if(accounts[i].acc_no == acc_no) {
                        if(accounts[i].balance >= amount) {
                            accounts[i].balance -= amount;
                            printf("Withdrawn %.2lf. New Balance: %.2lf\n", amount, accounts[i].balance);
                        } else {
                            printf("Insufficient balance!\n");
                        }
                        break;
                    }
                }
                if(i==count) printf("Account not found!\n");
                break;

            case 5:
                {
                    int dest_acc;
                    printf("Enter Source Account Number: ");
                    scanf("%d", &acc_no);
                    printf("Enter Destination Account Number: ");
                    scanf("%d", &dest_acc);
                    printf("Enter Amount: ");
                    scanf("%lf", &amount);
                    int src_idx=-1, dest_idx=-1;
                    for(i=0; i<count; i++) {
                        if(accounts[i].acc_no == acc_no) src_idx = i;
                        if(accounts[i].acc_no == dest_acc) dest_idx = i;
                    }
                    if(src_idx==-1 || dest_idx==-1) {
                        printf("One or both accounts not found!\n");
                        break;
                    }
                    if(accounts[src_idx].balance >= amount) {
                        accounts[src_idx].balance -= amount;
                        accounts[dest_idx].balance += amount;
                        printf("Transferred %.2lf from %d to %d\n", amount, acc_no, dest_acc);
                    } else {
                        printf("Insufficient balance!\n");
                    }
                }
                break;

            case 6:
                printf("Enter Account Number to display: ");
                scanf("%d", &acc_no);
                for(i=0; i<count; i++) {
                    if(accounts[i].acc_no == acc_no) {
                        printf("Account No: %d\nName: %s\nBalance: %.2lf\n", accounts[i].acc_no, accounts[i].name, accounts[i].balance);
                        break;
                    }
                }
                if(i==count) printf("Account not found!\n");
                break;

            case 7:
                printf("All Accounts:\n");
                for(i=0; i<count; i++) {
                    printf("Acc: %d, Name: %s, Balance: %.2lf\n", accounts[i].acc_no, accounts[i].name, accounts[i].balance);
                }
                break;

            case 8:
                {
                    double rate;
                    printf("Enter interest rate in %%: ");
                    scanf("%lf", &rate);
                    for(i=0; i<count; i++) {
                        accounts[i].balance += (accounts[i].balance * rate / 100.0);
                    }
                    printf("Interest applied.\n");
                }
                break;

            case 9:
                printf("Monthly Statement:\n");
                for(i=0; i<count; i++) {
                    printf("Acc: %d, Name: %s, Balance: %.2lf\n", accounts[i].acc_no, accounts[i].name, accounts[i].balance);
                }
                break;

            case 0:
                printf("Exiting...\n");
                break;

            default:
                printf("Invalid choice!\n");
        }
    }

    return 0;
}
