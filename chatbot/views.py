from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication  # ✅ Correct Import
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import json
from .utils import *
from django.core.cache import cache
from authentication.utils import *
from authentication.models import *
from core_banking.models import *
from core_banking.utils import *
from decimal import Decimal


class RouterAPI(APIView):
    authentication_classes = [JWTAuthentication]  # ✅ Now this works
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """API to route user input to the appropriate function (JWT Protected)"""
        try:
            data = request.data  # DRF automatically parses JSON
            user_input = data.get("user_input", "")
            router_response = router(user_input)
            
            if router_response.get("point") == "transfer money":
                respone =  check_missing_info(extract_entities(user_input))
                return Response({"status": True, "data": respone.get("data"), "message": respone.get("message"), "route": router_response.get("point"), "next": router_response.get("point")}, status=200)

            elif router_response.get("point") == "bill payment":

                structure =  {"consumer_number": None, "bill_detail": None}
                unpaid_bills = Bill.objects.filter(user=request.user, payment_status=False)
                bills_data = [
                    {
                        "bill_type": bill.bill_type,
                        "company": bill.company,
                        "consumer_number": bill.consumer_number,
                        "amount": float(bill.amount),  # ensure it's JSON-serializable
                        "due_date": bill.due_date.isoformat(),  # format date as string
                    }
                    for bill in unpaid_bills
                ]

                if 'history' in request.data:
                    history = data.get("history")
                else:
                    history = []

                message_response = bill_status(structure, bills_data, user_input, history)

                history.append({"user": user_input, "assistant": message_response.get("message")})
                
                if message_response.get("consumer_number") and message_response.get("bill_detail"):    
                    return Response({"status": True, "data": {"consumer_number": message_response.get("consumer_number"), "bill_detail": message_response.get("bill_detail")}, "message": message_response.get("message"), "history": history, "route": "complete", "next": router_response.get("point")}, status=200)
                else:
                    return Response({"status": True, "data": {"consumer_number": message_response.get("consumer_number"), "bill_detail": message_response.get("bill_detail")}, "message": message_response.get("message"), "history": history, "route": "bill payment", "next": router_response.get("point")}, status=200)
            
            
            elif router_response.get("point") == "change password":

                llm_response = data.get("message", "")

                response = password_retriever(llm_response, user_input, change_password(user_input))
                return Response({"status": True, "data": response["updated_data"], "message": response["message"], "route": router_response.get("point"), "next": router_response.get("point")}, status=200)

            
            else:
                return Response({"status": True, "data": None, "message": router_response.get("message"), "route": router_response.get("point"), "next": "router"}, status=200)

        except json.JSONDecodeError:
            return Response({"status": False, "data": None, "message": "Invalid JSON format"}, status=400)
        except Exception as e:
            return Response({"status": False, "data": None, "message": str(e)}, status=500)

        
class TransferAPI(APIView):
    authentication_classes = [JWTAuthentication]  # ✅ Now this works
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """API to extract structured data from user input (JWT Protected)"""
        try:

            user_id = request.user.id
            user = User.objects.get(id=user_id)
            user_email = user.email
            data = request.data  # DRF automatically parses JSON
            input_data = data.get("data", "")
            user_input = data.get("user_input", "")
            message = data.get("message", "")

            if data.get("route") == "transfer money":
                respone =  check_missing_info(update_json_data(input_data, user_input, message,user_id))

                
                if respone.get("message") == "Completed":
                    respone = confirmation({"data": respone.get("data"), "user_input":None})
                    return Response({"status": True, "data": respone.get("data"), "message": respone.get("confirmation_message"), "route":"complete", "next":"transfer money"}, status=200)

                elif respone.get("message") == "Cancelled":
                    return Response({"status": True, "data": None, "message": "Transaction cancelled.", "route":None, "next":"router"}, status=200)
                               
                else:
                    return Response({"status": True, "data": respone.get("data"), "message": respone.get("message"), "route":"transfer money", "next":"transfer money"}, status=200)
                
            if data.get("route") == "complete":
                    respone = confirmation({"data": input_data, "user_input":user_input})

                    if respone.get("confirmation_message") in ["Proceed.", "Proceed"]:

                        otp = generate_otp()
                        cache.set(f"otp_{user_id}", otp, timeout=300)  # 5 min expiry
                        send_user_registration_emails("mushafmughal12@gmail.com", otp)

                        return Response({
                            "status": True,
                            "data": respone.get("data"),
                            "message": "An OTP has been sent to your email. Please verify it. To cancel, type 'exit'",
                            "route": "otp verification",
                            "next": "transfer money",
                        }, status=200)
                    
                    elif respone.get("confirmation_message") in ["Cancelled", "Cancelled."]:
                        
                        return Response({"status": True, "data": None, "message": "Transaction cancelled.", "route":None, "next":"router"}, status=200)

                    else:
                        return Response({"status": True, "data": respone.get("data"), "message": respone.get("confirmation_message"), "route":"complete", "next": "transfer money"}, status=200)
                    
            if data.get("route") == "otp verification":

                final_data = data.get("data")
                stored_otp = cache.get(f"otp_{user_id}")
                user_otp = data.get("user_input", None)

                if user_otp.lower().strip(".") not in ["exit", "cancel"]:

                    if not stored_otp:
                        return Response({"status": True, "data": final_data, "message": "OTP expired. Please request a new OTP.", "route":"otp verification", "next":"transfer money"}, status=200)
                    else:
                        if stored_otp == user_otp:
                            cache.delete(f"otp_{user_id}")  # Delete OTP from cache after successful verification

                            recipient_account_number = final_data.get("account_number")
                            amount = final_data.get("amount")
                            amount = Decimal(str(amount))
                            cleaned_account_number = recipient_account_number.replace(" ", "")
                            recipient_account = BankAccount.objects.get(account_number=cleaned_account_number)
                            sender_account = BankAccount.objects.get(user=user)

                            # 🔐 Optional: add service fee logic here if needed
                            service_fee = Decimal("0.00")
                            total_amount = amount + service_fee

                            # 🔄 Update balances
                            sender_account.balance -= total_amount
                            recipient_account.balance += amount
                            sender_account.save()
                            recipient_account.save()
                            tx_id = generate_unique_transaction_id()

                            # 🧾 Log debit (sender)
                            sender_transaction = Transaction.objects.create(
                                user=user,
                                transaction_id=tx_id,
                                stan=generate_unique_stan(),
                                rrn=generate_unique_rrn(),
                                transaction_type="debit",
                                amount=amount,
                                service_fee=service_fee,
                                total_amount=total_amount,
                                source_account_title=user.name,
                                source_bank=sender_account.bank_name,
                                source_account_number=sender_account.account_number,
                                destination_account_title=recipient_account.user.name,
                                destination_bank=recipient_account.bank_name,
                                destination_account_number=recipient_account.account_number,
                                channel="Raast"
                            )

                            # 🧾 Log credit (recipient)
                            receiver_transaction = Transaction.objects.create(
                                user=recipient_account.user,
                                transaction_id=tx_id,
                                stan=generate_unique_stan(),
                                rrn=generate_unique_rrn(),
                                transaction_type="credit",
                                amount=amount,
                                service_fee=Decimal("0.00"),
                                total_amount=amount,
                                source_account_title=user.name,
                                source_bank=sender_account.bank_name,
                                source_account_number=sender_account.account_number,
                                destination_account_title=recipient_account.user.name,
                                destination_bank=recipient_account.bank_name,
                                destination_account_number=recipient_account.account_number,
                                channel="Raast"
                            )

                            response_data = {
                                "sender": {
                                    "transaction_id": sender_transaction.transaction_id,
                                    "stan": sender_transaction.stan,
                                    "rrn": sender_transaction.rrn,
                                    "transaction_type": sender_transaction.transaction_type,
                                    "amount": str(sender_transaction.amount),
                                    "service_fee": str(sender_transaction.service_fee),
                                    "total_amount": str(sender_transaction.total_amount),
                                    "source_account_title": sender_transaction.source_account_title,
                                    "source_bank": sender_transaction.source_bank,
                                    "source_account_number": sender_transaction.source_account_number,
                                    "destination_account_title": sender_transaction.destination_account_title,
                                    "destination_bank": sender_transaction.destination_bank,
                                    "destination_account_number": sender_transaction.destination_account_number,
                                    "channel": sender_transaction.channel,
                                },
                                "receiver": {
                                    "transaction_id": receiver_transaction.transaction_id,
                                    "stan": receiver_transaction.stan,
                                    "rrn": receiver_transaction.rrn,
                                    "transaction_type": receiver_transaction.transaction_type,
                                    "amount": str(receiver_transaction.amount),
                                    "service_fee": str(receiver_transaction.service_fee),
                                    "total_amount": str(receiver_transaction.total_amount),
                                    "source_account_title": receiver_transaction.source_account_title,
                                    "source_bank": receiver_transaction.source_bank,
                                    "source_account_number": receiver_transaction.source_account_number,
                                    "destination_account_title": receiver_transaction.destination_account_title,
                                    "destination_bank": receiver_transaction.destination_bank,
                                    "destination_account_number": receiver_transaction.destination_account_number,
                                    "channel": receiver_transaction.channel,
                                }
                            }

                            response_data = {
                                "sender": {
                                    "transaction_id": sender_transaction.transaction_id,
                                    "stan": sender_transaction.stan,
                                    "rrn": sender_transaction.rrn,
                                    "transaction_type": sender_transaction.transaction_type,
                                    "amount": str(sender_transaction.amount),
                                    "service_fee": str(sender_transaction.service_fee),
                                    "total_amount": str(sender_transaction.total_amount),
                                    "source_account_title": sender_transaction.source_account_title,
                                    "source_bank": sender_transaction.source_bank,
                                    "source_account_number": sender_transaction.source_account_number,
                                    "destination_account_title": sender_transaction.destination_account_title,
                                    "destination_bank": sender_transaction.destination_bank,
                                    "destination_account_number": sender_transaction.destination_account_number,
                                    "channel": sender_transaction.channel,
                                },
                                "receiver": {
                                    "transaction_id": receiver_transaction.transaction_id,
                                    "stan": receiver_transaction.stan,
                                    "rrn": receiver_transaction.rrn,
                                    "transaction_type": receiver_transaction.transaction_type,
                                    "amount": str(receiver_transaction.amount),
                                    "service_fee": str(receiver_transaction.service_fee),
                                    "total_amount": str(receiver_transaction.total_amount),
                                    "source_account_title": receiver_transaction.source_account_title,
                                    "source_bank": receiver_transaction.source_bank,
                                    "source_account_number": receiver_transaction.source_account_number,
                                    "destination_account_title": receiver_transaction.destination_account_title,
                                    "destination_bank": receiver_transaction.destination_bank,
                                    "destination_account_number": receiver_transaction.destination_account_number,
                                    "channel": receiver_transaction.channel,
                                }
                            }

                            return Response({"status": True, "data": response_data, "message": "OTP verified successfully. Your transaction has been paid.", "route":None, "next":"router"}, status=200)
                        
                        elif stored_otp and stored_otp != user_otp:
                            return Response({"status": True, "data": final_data, "message": "Incorrect OTP. Please try again or type 'exit' to cancel.", "route":"otp verification", "next":"transfer money"}, status=200)
                        
                        else:
                            return Response({"status": True, "data": final_data, "message": "OTP verification failed due to an unknown error. Please try again or type 'exit' to cancel.", "route":"otp verification", "next":"transfer money"}, status=200)

                else:
                    return Response({"status": True, "data": None, "message": "Operation canceled.", "route":None, "next":"router"}, status=200)
                

        except json.JSONDecodeError:
            return Response({"status": False, "data": None, "message": "Invalid JSON format", "next": "router" }, status=400)
        except Exception as e: 
            return Response({"status": False, "data": None, "message": str(e), "next":"router"}, status=500)


class PayBillAPI(APIView):
    authentication_classes = [JWTAuthentication]  # ✅ Now this works
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """API to route user input to the appropriate function (JWT Protected)"""
        try:
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            user_email = user.email
            data = request.data  # DRF automatically parses JSON
            user_input = data.get("user_input", "")
            history = data.get("history")
            
            if data.get("route") == "bill payment":
                
                structure =  {"consumer_number": None, "bill_detail": None}
                unpaid_bills = Bill.objects.filter(user=request.user, payment_status=False)
                bills_data = [
                    {
                        "bill_type": bill.bill_type,
                        "company": bill.company,
                        "consumer_number": bill.consumer_number,
                        "amount": float(bill.amount),  # ensure it's JSON-serializable
                        "due_date": bill.due_date.isoformat(),  # format date as string
                    }
                    for bill in unpaid_bills
                ]

                message_response = bill_status(structure, bills_data, user_input, history)
                history.append({"user": user_input, "assistant": message_response.get("message")})
                

                if message_response["consumer_number"] and message_response.get("bill_detail") and message_response.get("message") in ["proceed", "proceed.", "Proceed", "Proceed."]:
                    
                    otp = generate_otp()
                    cache.set(f"otp_{user_id}", otp, timeout=300)  # 5 min expiry
                    send_user_registration_emails("mushafmughal12@gmail.com", otp)
                    f_data = {"consumer_number": message_response.get("consumer_number"), "bill_detail": message_response.get("bill_detail")}

                    return Response({"status": True, "data": f_data, "message": "An OTP has been sent to your email. Please verify it. To cancel, type 'exit'", "history": history, "route": "otp verification", "next": "bill payment"}, status=200)
                
                else:
                    return Response({"status": True, "data": {"consumer_number": message_response.get("consumer_number"), "bill_detail": message_response.get("bill_detail")}, "message": message_response.get("message"), "history": history, "route": "bill payment", "next": "bill payment"}, status=200)
            
            if data.get("route") == "otp verification":
                
                final_data = data.get("data")
                stored_otp = cache.get(f"otp_{user_id}")
                user_otp = data.get("user_input", None)

                if user_otp.lower().strip(".") not in ["exit", "cancel"]:

                    if not stored_otp:
                        return Response({"status": True, "data": final_data, "message": "OTP expired. Please request a new OTP.", "route":"otp verification", "next":"bill payment"}, status=200)
                    else:
                        if stored_otp == user_otp:
                            cache.delete(f"otp_{user_id}")  # Delete OTP from cache after successful verification


                            sender_account = BankAccount.objects.get(user=user)
                            bill = final_data["bill_detail"]
                            amount = Decimal(bill["amount"])
                            service_fee = Decimal("1.00")
                            total_amount = amount + service_fee
                            tx_id = generate_unique_transaction_id()

                            Transaction.objects.create(
                                user=user,
                                transaction_id=tx_id,
                                stan=generate_unique_stan(),
                                rrn=generate_unique_rrn(),
                                transaction_type="bill_payment",
                                amount=amount,
                                service_fee=service_fee,
                                total_amount=total_amount,
                                source_account_title=user.name,
                                source_bank=sender_account.bank_name,
                                source_account_number=sender_account.account_number,
                                destination_account_title=f"{bill['company']} ({bill['bill_type']})",
                                destination_bank="Utility Billing",  # or a specific bank if known
                                destination_account_number="********",  # Masked account number
                                channel="Raast"
                            )
                            
                            return Response({"status": True, "data": final_data, "message": "OTP verified successfully. Your bill has been paid.", "route":None, "next":"router"}, status=200)
                        
                        elif stored_otp and stored_otp != user_otp:
                            return Response({"status": True, "data": None, "message": "Incorrect OTP. Please try again or type 'exit' to cancel.", "route":"otp verification", "next":"bill payment"}, status=200)
                        
                        else:
                            return Response({"status": True, "data": None, "message": "OTP verification failed due to an unknown error. Please try again or type 'exit' to cancel.", "route":"otp verification", "next":"bill payment"}, status=200)

                else:
                    return Response({"status": True, "data": None, "message": "Operation canceled.", "route":None, "next":"router"}, status=200)


        except json.JSONDecodeError:
            return Response({"status": False, "data": None, "message": "Invalid JSON format", "next": "router" }, status=400)
        except Exception as e: 
            return Response({"status": False, "data": None, "message": str(e), "next":"router"}, status=500)



class ChangePasswordAPI(APIView):
    authentication_classes = [JWTAuthentication]  # ✅ Now this works
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """API to route user input to the appropriate function (JWT Protected)"""
        try:
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            user_email = user.email
            data = request.data  # DRF automatically parses JSON
            
            llm_response = data.get("message", "")
            user_input = data.get("user_input", "")
            input_data = data.get("data", "")

            
            if data.get("route") == "change password":
                response = password_retriever(llm_response,user_input,input_data)

                if response["message"] in ["allowed"]:
                    return Response({"status": True, "data": response["updated_data"], "message": "Would you like to proceed with these changes? Please type 'yes' or 'no' to confirm.", "route": "complete", "next":"change password"}, status=200)
                else:
                    return Response({"status": True, "data": response["updated_data"], "message": response["message"], "route": "change password", "next":"change password"}, status=200)

            if data.get("route") == "complete":

                if user_input.lower().strip(".") in ["yes", "proceed", "confirm", "ok"]:
                        # Update password in the database
                        user.set_password(input_data["new_password"])
                        user.save()
                        return Response({"status": True, "data": None, "message":"Your password has been changed successfully!", "route": None, "next":"router"}, status=200)
                
                elif user_input.lower().strip(".") in ["no", "cancel", "exit", "nope"]:
                    return Response({"status": True, "data": None, "message": "Operation cancelled!", "route": None, "next":"router"}, status=200)
                else:
                    return Response({"status": True, "data": None, "message": "Invalid response. Please type 'yes' or 'no'.", "route": "complete", "next":"change password"}, status=200)

        except json.JSONDecodeError:
            return Response({"status": False, "data": None, "message": "Invalid JSON format", "next": "router" }, status=400)
        except Exception as e: 
            return Response({"status": False, "data": None, "message": str(e), "next":"router"}, status=500)