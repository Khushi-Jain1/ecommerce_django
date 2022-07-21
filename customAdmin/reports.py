from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views import View
from Ecommerce.settings import MEDIA_URL
from customAdmin.decorators import unauthenticated_admin
from customAdmin.forms import ReportForm, SalesReportForm
from customAdmin.models import Coupons, User
from customUser.models import CouponUsage, OrderProductDetails, Orders
import pytz
from django.db.models import Sum
import logging


class Report(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    login_url = 'admin:login'
    template_name = 'customAdmin/reports.html'
    form_class = ReportForm
    success_url = reverse_lazy('admin:reports')
    permission_required = 'user.is_superuser'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = {'title': 'Reports'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        context['table'] = {
            'columns': ['Date Started', 'Date End', 'No. Orders', 'No. Products', 'Total'], }
        context['form'] = {'report_form': ReportForm,
                           'filter_form': SalesReportForm}

        return context

    def form_valid(self, form):
        try:
            form = ReportForm(self.request.POST or None)
            if form.is_valid():
                report = form.cleaned_data.get('report_type')
                context = {}
                context['form'] = form
                context['tab'] = {'title': 'Reports'}
                context['user'] = {'username': self.request.user.username,
                                'media': MEDIA_URL, 'image': self.request.user.image}
                if report == str(1):  # sales report
                    return redirect('admin:sales_report')
                elif report == str(2):  # customer report
                    return redirect('admin:customers_report')
                elif report == str(3):  # customer report
                    return redirect('admin:coupons_report')
            return super().form_valid(form)
        except Exception as e:
            logging.error(e)


class CustomerReport(LoginRequiredMixin,PermissionRequiredMixin, TemplateView):
    login_url = 'admin:login'
    template_name = 'customAdmin/sales.html'
    permission_required = 'user.is_superuser'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = {'title': 'Reports'}
        context['report'] = 'customer'
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        context['table'] = {
            'columns': ['Start Date', 'End Date', 'No. Customer'], }
        report_form = ReportForm()
        report_form.fields['report_type'].initial = 2
        context['form'] = {'report_form': report_form,
                           'filter_form': SalesReportForm}
        return context

    def post(self, request):
        context = {}
        try:
            filter_form = SalesReportForm(request.POST or None)
            context['tab'] = {'title': 'Reports'}
            context['user'] = {'username': self.request.user.username,
                            'media': MEDIA_URL, 'image': self.request.user.image}
            if filter_form.is_valid():
                group_by = filter_form.cleaned_data.get('groupby')
                startDate = request.POST.get('startDate')
                endDate = request.POST.get('endDate')
                start_date = datetime.strptime(startDate, '%m/%d/%Y')
                end_date = datetime.strptime(endDate, '%m/%d/%Y')
                dates = []
                a = pytz.utc.localize(start_date)
                c = pytz.utc.localize(end_date)
                while a < c:
                    b = a + timedelta(days=int(group_by))
                    if b > c:
                        b = c
                    dates.append({
                        'startDate': a,
                        'endDate': b,
                        'customers': User.objects.filter(date_joined__range=[a, b], is_superuser=False).count(),
                    })
                    a = b
                context['date'] = {'startDate': startDate, 'endDate': endDate}
            else:
                messages.error(request,filter_form.errors)
            context['table'] = {
                'columns': ['Start Date', 'End Date', 'No. Customer'],
                'data': dates}
            report_form = ReportForm()
            report_form.fields['report_type'].initial = 2
            context['form'] = {'report_form': report_form,
                            'filter_form': filter_form}
            return render(request, 'customAdmin/sales.html', context)
        except Exception as e:
            logging.error(e)


class CouponReport(LoginRequiredMixin,PermissionRequiredMixin, TemplateView):
    login_url = 'admin:login'
    template_name = 'customAdmin/sales.html'
    permission_required = 'user.is_superuser'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = {'title': 'Reports'}
        context['report'] = 'coupon'
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        context['table'] = {
            'columns': ['Start Date', 'End Date', 'Coupon Name', 'Code', 'Orders'], }
        report_form = ReportForm()
        report_form.fields['report_type'].initial = 3
        context['form'] = {'report_form': report_form,
                           'filter_form': SalesReportForm}
        return context
    
    def post(self, request):
        context = {}
        context['report'] = 'coupon'
        try:
            context['tab'] = {'title': 'Reports'}
            context['user'] = {'username': self.request.user.username,
                            'media': MEDIA_URL, 'image': self.request.user.image}
            filter_form = SalesReportForm(request.POST or None)
            if filter_form.is_valid():
                group_by = filter_form.cleaned_data.get('groupby')
                startDate = request.POST.get('startDate')
                endDate = request.POST.get('endDate')
                start_date = datetime.strptime(startDate, '%m/%d/%Y')
                end_date = datetime.strptime(endDate, '%m/%d/%Y')
                dates = []
                a = pytz.utc.localize(start_date)
                c = pytz.utc.localize(end_date)
                while a < c:
                    b = a + timedelta(days=int(group_by))
                    if b > c:
                        b = c
                    for coupon in CouponUsage.objects.values('coupon_id').distinct():
                        dates.append({
                            'startDate': a,
                            'endDate': b,
                            'orders': CouponUsage.objects.filter(used_at__range=[a, b], coupon_id = coupon['coupon_id']).count(),
                            'name': Coupons.objects.get(id = coupon['coupon_id']).name,
                            'code': Coupons.objects.get(id = coupon['coupon_id']).code,

                        })
                    a = b
                context['date'] = {'startDate': startDate, 'endDate': endDate}
            else:
                messages.error(request,filter_form.errors)
            context['table'] = {
                'columns':  ['Start Date', 'End Date', 'Coupon Name', 'Code', 'Orders'],
                'data': dates}
            report_form = ReportForm()
            report_form.fields['report_type'].initial = 3
            context['form'] = {'report_form': report_form,
                            'filter_form': filter_form}
            return render(request, 'customAdmin/sales.html', context)
        except Exception as e:
            logging.error(e)



class SalesReport(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url = 'admin:login'
    template_name = 'customAdmin/sales.html'
    permission_required = 'user.is_superuser'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = {'title': 'Reports'}
        context['report'] = 'sales'
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        context['table'] = {
            'columns': ['Date Started', 'Date End', 'No. Orders', 'No. Products', 'Total'], }
        report_form = ReportForm()
        report_form.fields['report_type'].initial = 1
        context['form'] = {'report_form': report_form,
                           'filter_form': SalesReportForm}
        return context

    def post(self, request):
        context = {}
        context['report'] = 'sales'
        try:
            context['tab'] = {'title': 'Reports'}
            context['user'] = {'username': self.request.user.username,
                            'media': MEDIA_URL, 'image': self.request.user.image}
            filter_form = SalesReportForm(request.POST or None)
            if filter_form.is_valid():
                group_by = filter_form.cleaned_data.get('groupby')
                startDate = request.POST.get('startDate')
                endDate = request.POST.get('endDate')
                start_date = datetime.strptime(startDate, '%m/%d/%Y')
                end_date = datetime.strptime(endDate, '%m/%d/%Y')
                dates = []
                a = pytz.utc.localize(start_date)
                c = pytz.utc.localize(end_date)
                while a < c:
                    b = a + timedelta(days=int(group_by))
                    if b > c:
                        b = c
                    products = 0
                    for order in Orders.objects.filter(order_date__range=[a, b]):
                        count = OrderProductDetails.objects.filter(order_id=order.id).aggregate(Sum('quantity'))['quantity__sum'] or 0
                        products = products + count
                    dates.append({
                        'startDate': a,
                        'endDate': b,
                        'orders': Orders.objects.filter(order_date__range=[a, b]).count(),
                        'products': products,
                        'total': Orders.objects.filter(order_date__range=[a, b]).aggregate(Sum('subtotal'))['subtotal__sum'] or 0
                    })
                    a = b
                context['date'] = {'startDate': startDate, 'endDate': endDate}
            else:
                messages.error(request,filter_form.errors)
            context['table'] = {
                'columns': ['Date Started', 'Date End', 'No. Orders', 'No. Products', 'Total'],
                'data': dates}
            report_form = ReportForm()
            report_form.fields['report_type'].initial = 1
            context['form'] = {'report_form': report_form,
                            'filter_form': filter_form}
        except Exception as e:
            logging.error(e)
        return render(request, 'customAdmin/sales.html', context)
