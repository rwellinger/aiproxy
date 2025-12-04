import {Component, inject, Input, OnInit} from "@angular/core";
import {CommonModule} from "@angular/common";
import {HttpClient} from "@angular/common/http";
import {firstValueFrom} from "rxjs";
import {ApiConfigService} from "../../services/config/api-config.service";
import {NotificationService} from "../../services/ui/notification.service";
import {MatSnackBarModule} from "@angular/material/snack-bar";
import {TranslateModule, TranslateService} from "@ngx-translate/core";

@Component({
    selector: "app-song-profile",
    standalone: true,
    imports: [CommonModule, MatSnackBarModule, TranslateModule],
    templateUrl: "./song-profile.component.html",
    styleUrl: "./song-profile.component.scss"
})
export class SongProfileComponent implements OnInit {
    @Input() isEmbedded: boolean = false;

    isLoading = true;
    billingInfo: any = null;

    private apiConfig = inject(ApiConfigService);
    private notificationService = inject(NotificationService);
    private http = inject(HttpClient);
    private translate = inject(TranslateService);

    ngOnInit() {
        this.loadBillingInfo();
    }

    async loadBillingInfo() {
        this.isLoading = true;
        try {
            this.billingInfo = await firstValueFrom(
                this.http.get<any>(this.apiConfig.endpoints.billing.info)
            );
        } catch (error) {
            console.error("Error loading billing info:", error);
            this.notificationService.error(this.translate.instant("songProfile.notifications.loadError"));
            this.billingInfo = null;
        } finally {
            this.isLoading = false;
        }
    }

    formatCurrency(amount: number): string {
        return (amount / 100).toFixed(2);
    }

    getStatusClass(status: string): string {
        if (!status) return "status-unknown";

        switch (status.toLowerCase()) {
            case "active":
            case "good":
                return "status-active";
            case "inactive":
            case "suspended":
                return "status-inactive";
            case "pending":
                return "status-pending";
            default:
                return "status-unknown";
        }
    }

    getStatusIcon(status: string): string {
        if (!status) return "fa-question-circle";

        switch (status.toLowerCase()) {
            case "active":
            case "good":
                return "fa-check-circle";
            case "inactive":
            case "suspended":
                return "fa-times-circle";
            case "pending":
                return "fa-clock";
            default:
                return "fa-question-circle";
        }
    }
}
