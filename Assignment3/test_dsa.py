import dsa
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['normal', 'attacker'], required=True, help='Test DSA normally or as an attacker')
    args = parser.parse_args()

    if args.mode == 'normal':
        p, q, g = dsa.gen_pubkeys(L=512) # User 1 generates shared global public key values
        x, y = dsa.gen_userkeys(p, q ,g) # User 1 generates private and public keys
        message = input("(User1) Message: ")
        r, s, message = dsa.sign_message(message, p, q, g, x) # User 1 signs message
        print(f'(User1) have now signed the message and generated these numbers:\nr: {r}\ns: {s}')

        # User 2 will now verify the message it receives from User 1
        print(f'\n\n********** (User2) has reveived the message and will now verify it **********')
        verified = dsa.verify_message(message, p, q, g, r, s, y)
        if verified:
            print("The message was verified!")
        else:
            print("The message was not verifed..")
    
    elif args.mode == 'attacker':
        p, q, g = dsa.gen_pubkeys(L=512) # User 1 generates shared global public key values
        x, y = dsa.gen_userkeys(p, q ,g) # User 1 generates private and public keys
        message = input("(User1) Message: ")
        r, s, message = dsa.sign_message(message, p, q, g, x) # User 1 signs message
        print(f'(User1) have now signed the message and generated these numbers:\nr: {r}\ns: {s}')
        delim = '#'*20
        print(f'{delim } ATTACKER INTERUPTS {delim}\nEdit the original message')
        message = input('(Attacker) Edit message: ')

        # User 2 will now verify the faked message it receives from the attacker
        print(f'\n\n********** (User2) has reveived the message and will now verify it **********')
        verified = dsa.verify_message(message, p, q, g, r, s, y)
        if verified:
            print("The message was verified!")
        else:
            print("The message was not verifed..")






